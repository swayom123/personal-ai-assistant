import logging
import re
import subprocess
from pathlib import Path
from typing import List, Tuple
from backend.app.schemas.voice import AudioDevice, AudioDevicesResponse

logger = logging.getLogger("app.voice.devices")

class AudioDevicesService:
    def get_audio_devices(self) -> AudioDevicesResponse:
        inputs: List[AudioDevice] = []
        outputs: List[AudioDevice] = []

        # 1. Try parsing /proc/asound/pcm (fast, no subprocess)
        pcm_path = Path("/proc/asound/pcm")
        cards_path = Path("/proc/asound/cards")

        if pcm_path.exists():
            try:
                card_names = {}
                if cards_path.exists():
                    card_content = cards_path.read_text(encoding="utf-8", errors="ignore")
                    # Match " 0 [sofhdadsp      ]: sof-hda-dsp - sof-hda-dsp"
                    for match in re.finditer(r"^\s*(\d+)\s+\[(\w+)\]:\s+(.+)$", card_content, re.MULTILINE):
                        card_names[match.group(1)] = match.group(2)

                pcm_content = pcm_path.read_text(encoding="utf-8", errors="ignore")
                for line in pcm_content.strip().splitlines():
                    # Line format: 00-00: HDA Analog (*) :  : playback 1 : capture 1
                    parts = line.split(":")
                    if len(parts) >= 3:
                        dev_id = parts[0].strip()
                        raw_name = parts[1].strip()
                        clean_name = re.sub(r"\s*\(\*\)", "", raw_name).strip()
                        
                        card_num = dev_id.split("-")[0].lstrip("0") or "0"
                        card_label = card_names.get(card_num, f"Card {card_num}")
                        display_name = f"{clean_name} ({card_label})" if clean_name else f"Audio Device {dev_id}"

                        info_str = ":".join(parts[2:]).lower()
                        if "capture" in info_str:
                            inputs.append(AudioDevice(
                                id=f"hw:{dev_id}",
                                name=f"Microphone: {display_name}",
                                is_default=len(inputs) == 0,
                                type="input",
                                channels=2,
                                sample_rate=16000 if "16khz" in clean_name.lower() else 44100
                            ))
                        if "playback" in info_str:
                            outputs.append(AudioDevice(
                                id=f"hw:{dev_id}",
                                name=f"Speaker: {display_name}",
                                is_default=len(outputs) == 0,
                                type="output",
                                channels=2,
                                sample_rate=44100
                            ))
            except Exception as e:
                logger.warning(f"Error parsing /proc/asound: {e}")

        # 2. If nothing detected from proc, try arecord / aplay
        if not inputs or not outputs:
            arecord_inputs, aplay_outputs = self._query_alsa_cli()
            if not inputs and arecord_inputs:
                inputs = arecord_inputs
            if not outputs and aplay_outputs:
                outputs = aplay_outputs

        # 3. Always guarantee default fallback devices
        if not inputs:
            inputs.append(AudioDevice(
                id="default",
                name="Default System Microphone",
                is_default=True,
                type="input",
                channels=2,
                sample_rate=44100
            ))

        if not outputs:
            outputs.append(AudioDevice(
                id="default",
                name="Default System Audio Output / Speakers",
                is_default=True,
                type="output",
                channels=2,
                sample_rate=44100
            ))

        default_in = next((d.id for d in inputs if d.is_default), inputs[0].id)
        default_out = next((d.id for d in outputs if d.is_default), outputs[0].id)

        return AudioDevicesResponse(
            inputs=inputs,
            outputs=outputs,
            default_input=default_in,
            default_output=default_out
        )

    def _query_alsa_cli(self) -> Tuple[List[AudioDevice], List[AudioDevice]]:
        inputs = []
        outputs = []
        try:
            res_rec = subprocess.run(["arecord", "-l"], capture_output=True, text=True, timeout=2)
            if res_rec.returncode == 0:
                for line in res_rec.stdout.splitlines():
                    # card 0: sofhdadsp [sof-hda-dsp], device 0: HDA Analog (*) []
                    m = re.search(r"card\s+(\d+):.*device\s+(\d+):\s+([^\[\(]+)", line)
                    if m:
                        c, d, name = m.group(1), m.group(2), m.group(3).strip()
                        inputs.append(AudioDevice(
                            id=f"hw:{c},{d}",
                            name=f"Microphone: {name} (Card {c})",
                            is_default=len(inputs) == 0,
                            type="input",
                            channels=2,
                            sample_rate=44100
                        ))
        except Exception:
            pass

        try:
            res_play = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=2)
            if res_play.returncode == 0:
                for line in res_play.stdout.splitlines():
                    m = re.search(r"card\s+(\d+):.*device\s+(\d+):\s+([^\[\(]+)", line)
                    if m:
                        c, d, name = m.group(1), m.group(2), m.group(3).strip()
                        outputs.append(AudioDevice(
                            id=f"hw:{c},{d}",
                            name=f"Speaker: {name} (Card {c})",
                            is_default=len(outputs) == 0,
                            type="output",
                            channels=2,
                            sample_rate=44100
                        ))
        except Exception:
            pass

        return inputs, outputs

devices_service = AudioDevicesService()
