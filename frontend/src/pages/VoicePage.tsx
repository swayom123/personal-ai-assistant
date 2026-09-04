import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Radio,
  Play,
  Sliders,
  AlertCircle,
  AudioWaveform,
  Save,
  MessageSquare,
} from 'lucide-react';
import { apiService } from '../services/api';
import {
  VoiceState,
  AudioDevice,
  VoiceSettings,
  VoiceInfo,
  VoiceInteractionResponse,
} from '../types/api';

interface InteractionHistoryItem {
  id: string;
  transcript: string;
  text_response: string;
  audio_url?: string;
  duration_ms: number;
  timestamp: string;
}

export const VoicePage: React.FC = () => {
  // Voice State
  const [voiceState, setVoiceState] = useState<VoiceState>('IDLE');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Settings & Devices
  const [showSettings, setShowSettings] = useState(false);
  const [devices, setDevices] = useState<{ inputs: AudioDevice[]; outputs: AudioDevice[] }>({
    inputs: [],
    outputs: [],
  });
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const [settings, setSettings] = useState<VoiceSettings>({
    microphone: 'default',
    speaker: 'default',
    voice: 'en_US-lessac-medium',
    speed: 1.0,
    volume: 1.0,
    wake_word: 'Hey Max',
    assistant_name: 'Max',
    language: 'en',
    tts_provider: 'piper',
    stt_model: 'base',
    vad_filter: true,
  });
  const [settingsSavedToast, setSettingsSavedToast] = useState(false);

  // History & Playback
  const [history, setHistory] = useState<InteractionHistoryItem[]>([]);
  const [activeAudioPlaying, setActiveAudioPlaying] = useState<string | null>(null);
  const [wakeWordTriggered, setWakeWordTriggered] = useState(false);

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const currentAudioElementRef = useRef<HTMLAudioElement | null>(null);

  // 1. Initial Data Loading
  useEffect(() => {
    // Load devices
    apiService
      .getVoiceDevices()
      .then((res) => {
        setDevices({ inputs: res.inputs, outputs: res.outputs });
      })
      .catch((err) => console.error('Failed to load audio devices:', err));

    // Load voices
    apiService
      .getVoiceVoices()
      .then((res) => setVoices(res))
      .catch((err) => console.error('Failed to load voices:', err));

    // Load settings
    apiService
      .getVoiceSettings()
      .then((res) => setSettings(res))
      .catch((err) => console.error('Failed to load voice settings:', err));

    // Connect WebSocket for live state streaming
    connectWebSocket();

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (wsRef.current) wsRef.current.close();
      if (currentAudioElementRef.current) {
        currentAudioElementRef.current.pause();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const wsUrl = apiService.getVoiceWsUrl();
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'state_change' && data.state) {
            setVoiceState(data.state as VoiceState);
          } else if (data.type === 'wake_word_detected') {
            setWakeWordTriggered(true);
            setTimeout(() => setWakeWordTriggered(false), 3000);
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        // Attempt reconnect after 4 seconds if unmounted
        setTimeout(connectWebSocket, 4000);
      };
    } catch (e) {
      console.warn('WebSocket connection not initialized:', e);
    }
  };

  // 2. Microphone Recording
  const startRecording = async () => {
    setErrorMessage(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      audioChunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg',
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType || 'audio/webm',
        });
        stream.getTracks().forEach((track) => track.stop());
        await processAudioInteraction(audioBlob);
      };

      mediaRecorder.start(250);
      setIsRecording(true);
      setVoiceState('LISTENING');
      setRecordingSeconds(0);

      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err: unknown) {
      console.error('Microphone access failed:', err);
      setErrorMessage(
        'Could not access microphone. Please ensure microphone permissions are granted.'
      );
      setVoiceState('ERROR');
      setTimeout(() => setVoiceState('IDLE'), 3000);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      setVoiceState('PROCESSING');
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // 3. Process Interaction through Pipeline
  const processAudioInteraction = async (audioBlob: Blob) => {
    try {
      setVoiceState('PROCESSING');
      const response: VoiceInteractionResponse = await apiService.voiceInteract(audioBlob);

      let audioUrl: string | undefined = undefined;
      if (response.audio_base64) {
        audioUrl = `data:audio/wav;base64,${response.audio_base64}`;
        playAudio(audioUrl, response.conversation_id);
      }

      setHistory((prev) => [
        {
          id: response.conversation_id || String(Date.now()),
          transcript: response.transcript,
          text_response: response.text_response,
          audio_url: audioUrl,
          duration_ms: response.processing_time_ms,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
        ...prev,
      ]);

      setVoiceState(response.audio_base64 ? 'SPEAKING' : 'IDLE');
    } catch (err: unknown) {
      console.error('Voice pipeline interaction failed:', err);
      setErrorMessage((err as Error).message || 'Voice interaction failed');
      setVoiceState('ERROR');
      setTimeout(() => setVoiceState('IDLE'), 4000);
    }
  };

  // 4. Audio Playback
  const playAudio = (url: string, id?: string) => {
    if (currentAudioElementRef.current) {
      currentAudioElementRef.current.pause();
    }

    const audio = new Audio(url);
    currentAudioElementRef.current = audio;
    if (id) setActiveAudioPlaying(id);
    setVoiceState('SPEAKING');

    audio.onended = () => {
      setActiveAudioPlaying(null);
      setVoiceState('IDLE');
    };

    audio.onerror = () => {
      setActiveAudioPlaying(null);
      setVoiceState('IDLE');
    };

    audio.play().catch((e) => {
      console.warn('Autoplay prevented by browser:', e);
      setVoiceState('IDLE');
    });
  };

  const stopAudio = () => {
    if (currentAudioElementRef.current) {
      currentAudioElementRef.current.pause();
      setActiveAudioPlaying(null);
      setVoiceState('IDLE');
    }
  };

  // 5. Save Settings
  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await apiService.updateVoiceSettings(settings);
      setSettings(updated);
      setSettingsSavedToast(true);
      setTimeout(() => setSettingsSavedToast(false), 2500);
    } catch (err) {
      console.error('Failed to save settings:', err);
      setErrorMessage('Failed to save voice configuration');
    }
  };

  // Helper for voice state visuals
  const getStateBadge = (state: VoiceState) => {
    switch (state) {
      case 'LISTENING':
        return {
          label: 'LISTENING',
          color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
          dot: 'bg-emerald-400 animate-pulse',
        };
      case 'PROCESSING':
        return {
          label: 'PROCESSING',
          color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
          dot: 'bg-amber-400 animate-ping',
        };
      case 'SPEAKING':
        return {
          label: 'SPEAKING',
          color: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
          dot: 'bg-indigo-400 animate-bounce',
        };
      case 'ERROR':
        return {
          label: 'ERROR',
          color: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
          dot: 'bg-rose-400',
        };
      default:
        return {
          label: 'IDLE',
          color: 'bg-surface-subtle text-text-secondary border-border',
          dot: 'bg-text-secondary/50',
        };
    }
  };

  const stateVisual = getStateBadge(voiceState);

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12 animate-in fade-in duration-300">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-surface border border-border shadow-md">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">
              Voice Assistant
            </h1>
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-semibold border ${stateVisual.color}`}
            >
              <span className={`w-2 h-2 rounded-full ${stateVisual.dot}`} />
              {stateVisual.label}
            </span>
            {wakeWordTriggered && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-primary/20 border border-primary text-primary font-mono animate-pulse">
                Wake Word Detected!
              </span>
            )}
          </div>
          <p className="text-xs md:text-sm text-text-secondary mt-1">
            Duplex speech engine powered by Faster-Whisper, Piper TTS, and configurable Wake Word
            detection.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded-xl border transition-all ${
              showSettings
                ? 'bg-primary text-white border-primary shadow-sm'
                : 'bg-surface-subtle hover:bg-surface border-border text-text-secondary hover:text-text-primary'
            }`}
          >
            <Sliders className="w-4 h-4" />
            Voice Settings
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-xs text-rose-300 hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Interactive Stage */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visualizer & Mic Control (Left 7 cols) */}
        <div className="lg:col-span-7 flex flex-col items-center justify-center p-8 md:p-12 rounded-2xl bg-surface border border-border min-h-[420px] relative overflow-hidden text-center shadow-lg">
          {/* Animated Background Atmosphere */}
          <div
            className={`absolute inset-0 transition-opacity duration-700 pointer-events-none ${
              voiceState === 'LISTENING'
                ? 'bg-emerald-500/5 opacity-100'
                : voiceState === 'PROCESSING'
                ? 'bg-amber-500/5 opacity-100'
                : voiceState === 'SPEAKING'
                ? 'bg-indigo-500/5 opacity-100'
                : voiceState === 'ERROR'
                ? 'bg-rose-500/5 opacity-100'
                : 'opacity-0'
            }`}
          />

          {/* Central Animated Orb / Button */}
          <div className="relative mb-8">
            {/* Pulsing Aura Rings */}
            {voiceState === 'LISTENING' && (
              <>
                <div className="absolute -inset-4 rounded-full border-2 border-emerald-500/30 animate-ping" />
                <div className="absolute -inset-8 rounded-full border border-emerald-500/20 animate-pulse" />
              </>
            )}
            {voiceState === 'PROCESSING' && (
              <div className="absolute -inset-6 rounded-full border-2 border-dashed border-amber-400 animate-spin duration-3000" />
            )}
            {voiceState === 'SPEAKING' && (
              <div className="absolute -inset-6 rounded-full border-2 border-indigo-500/40 animate-pulse" />
            )}

            <button
              onClick={toggleRecording}
              disabled={voiceState === 'PROCESSING'}
              className={`w-36 h-36 md:w-44 md:h-44 rounded-full flex flex-col items-center justify-center shadow-2xl transition-all transform active:scale-95 focus:outline-none ${
                isRecording
                  ? 'bg-gradient-to-tr from-emerald-600 to-teal-400 text-white shadow-emerald-500/25 ring-8 ring-emerald-500/20'
                  : voiceState === 'SPEAKING'
                  ? 'bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-indigo-500/25 ring-8 ring-indigo-500/20'
                  : 'bg-gradient-to-tr from-surface-subtle to-surface border border-border hover:border-primary/50 text-text-primary shadow-black/20 hover:scale-105'
              }`}
            >
              {isRecording ? (
                <>
                  <MicOff className="w-10 h-10 md:w-12 md:h-12 animate-pulse" />
                  <span className="text-xs font-mono font-bold mt-2">
                    {recordingSeconds}s • STOP
                  </span>
                </>
              ) : voiceState === 'SPEAKING' ? (
                <>
                  <Volume2 className="w-10 h-10 md:w-12 md:h-12 animate-bounce" />
                  <span className="text-xs font-mono font-bold mt-2">SPEAKING</span>
                </>
              ) : voiceState === 'PROCESSING' ? (
                <>
                  <Radio className="w-10 h-10 md:w-12 md:h-12 animate-spin text-amber-400" />
                  <span className="text-xs font-mono font-bold mt-2 text-amber-400">
                    THINKING...
                  </span>
                </>
              ) : (
                <>
                  <Mic className="w-10 h-10 md:w-12 md:h-12 text-primary" />
                  <span className="text-xs font-semibold mt-2 text-text-secondary">
                    Click to Talk
                  </span>
                </>
              )}
            </button>
          </div>

          {/* Assistant Info & Wake Word Prompt */}
          <div className="space-y-2 z-10 max-w-md">
            <h2 className="text-lg font-bold text-text-primary">
              {isRecording
                ? 'Listening to speech...'
                : voiceState === 'PROCESSING'
                ? 'Faster-Whisper & AI Core Processing...'
                : voiceState === 'SPEAKING'
                ? 'Playing synthesized response...'
                : `Say "${settings.wake_word}" or tap to speak`}
            </h2>
            <p className="text-xs text-text-secondary leading-relaxed">
              Assistant Name: <span className="text-primary font-mono">{settings.assistant_name}</span>{' '}
              • TTS: <span className="font-mono">{settings.tts_provider.toUpperCase()}</span> • STT:{' '}
              <span className="font-mono">Faster-Whisper ({settings.stt_model})</span>
            </p>
          </div>

          {/* Quick Action Test Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-2.5 mt-6 z-10">
            <button
              onClick={() => {
                apiService
                  .speakText(`Hello ${settings.assistant_name || 'there'}, voice test passed.`, {
                    provider: settings.tts_provider,
                    voice: settings.voice,
                    speed: settings.speed,
                    volume: settings.volume,
                  })
                  .then((blob) => {
                    const url = URL.createObjectURL(blob);
                    playAudio(url);
                  })
                  .catch((e) => setErrorMessage(e.message));
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-subtle hover:bg-border text-text-secondary text-xs font-medium transition-colors"
            >
              <Volume2 className="w-3.5 h-3.5" />
              Test Speaker (TTS)
            </button>
            {voiceState === 'SPEAKING' && (
              <button
                onClick={stopAudio}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 text-xs font-medium transition-colors"
              >
                <VolumeX className="w-3.5 h-3.5" />
                Stop Audio
              </button>
            )}
          </div>
        </div>

        {/* Settings Drawer or Interaction History (Right 5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          {showSettings ? (
            /* Settings Panel */
            <div className="p-6 rounded-2xl bg-surface border border-border shadow-lg space-y-4 animate-in slide-in-from-right duration-200">
              <div className="flex items-center justify-between pb-3 border-b border-border">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-primary" />
                  <h3 className="text-sm font-bold text-text-primary">Voice Configuration</h3>
                </div>
                <button
                  onClick={() => setShowSettings(false)}
                  className="text-xs text-text-secondary hover:text-text-primary"
                >
                  Close
                </button>
              </div>

              <form onSubmit={handleSaveSettings} className="space-y-4 text-xs">
                {/* Microphone Selection */}
                <div>
                  <label className="block font-medium text-text-secondary mb-1">
                    Microphone Device
                  </label>
                  <select
                    value={settings.microphone || 'default'}
                    onChange={(e) => setSettings({ ...settings, microphone: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-text-primary text-xs focus:ring-1 focus:ring-primary focus:outline-none"
                  >
                    <option value="default">Default System Microphone</option>
                    {devices.inputs.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name} {d.is_default ? '(Default)' : ''}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Speaker Selection */}
                <div>
                  <label className="block font-medium text-text-secondary mb-1">
                    Speaker / Output Device
                  </label>
                  <select
                    value={settings.speaker || 'default'}
                    onChange={(e) => setSettings({ ...settings, speaker: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-text-primary text-xs focus:ring-1 focus:ring-primary focus:outline-none"
                  >
                    <option value="default">Default System Audio Output</option>
                    {devices.outputs.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name} {d.is_default ? '(Default)' : ''}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Wake Word & Assistant Name */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-medium text-text-secondary mb-1">
                      Wake Word
                    </label>
                    <input
                      type="text"
                      value={settings.wake_word}
                      onChange={(e) => setSettings({ ...settings, wake_word: e.target.value })}
                      placeholder="e.g. Hey Max"
                      className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-text-primary text-xs focus:ring-1 focus:ring-primary focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block font-medium text-text-secondary mb-1">
                      Assistant Name
                    </label>
                    <input
                      type="text"
                      value={settings.assistant_name}
                      onChange={(e) => setSettings({ ...settings, assistant_name: e.target.value })}
                      placeholder="e.g. Max"
                      className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-text-primary text-xs focus:ring-1 focus:ring-primary focus:outline-none"
                    />
                  </div>
                </div>

                {/* TTS Provider & Voice */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-medium text-text-secondary mb-1">
                      TTS Provider
                    </label>
                    <select
                      value={settings.tts_provider}
                      onChange={(e) => setSettings({ ...settings, tts_provider: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-text-primary text-xs focus:ring-1 focus:ring-primary focus:outline-none"
                    >
                      <option value="piper">Piper (Local ONNX)</option>
                      <option value="coqui">Coqui TTS</option>
                      <option value="mock">Built-in Synthetic</option>
                    </select>
                  </div>
                  <div>
                    <label className="block font-medium text-text-secondary mb-1">Voice</label>
                    <select
                      value={settings.voice}
                      onChange={(e) => setSettings({ ...settings, voice: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-text-primary text-xs focus:ring-1 focus:ring-primary focus:outline-none"
                    >
                      {voices
                        .filter(
                          (v) =>
                            v.provider === settings.tts_provider ||
                            settings.tts_provider === 'mock'
                        )
                        .map((v) => (
                          <option key={v.id} value={v.id}>
                            {v.name}
                          </option>
                        ))}
                    </select>
                  </div>
                </div>

                {/* Speech Speed & Volume Sliders */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="flex justify-between font-medium text-text-secondary mb-1">
                      <span>Speed</span>
                      <span className="font-mono text-primary">{settings.speed}x</span>
                    </div>
                    <input
                      type="range"
                      min="0.5"
                      max="2.0"
                      step="0.1"
                      value={settings.speed}
                      onChange={(e) =>
                        setSettings({ ...settings, speed: parseFloat(e.target.value) })
                      }
                      className="w-full accent-primary cursor-pointer"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between font-medium text-text-secondary mb-1">
                      <span>Volume</span>
                      <span className="font-mono text-primary">
                        {Math.round(settings.volume * 100)}%
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.05"
                      value={settings.volume}
                      onChange={(e) =>
                        setSettings({ ...settings, volume: parseFloat(e.target.value) })
                      }
                      className="w-full accent-primary cursor-pointer"
                    />
                  </div>
                </div>

                {/* Language & VAD Noise Filter */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-medium text-text-secondary mb-1">Language</label>
                    <select
                      value={settings.language}
                      onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl bg-surface-subtle border border-border text-text-primary text-xs focus:ring-1 focus:ring-primary focus:outline-none"
                    >
                      <option value="en">English (en)</option>
                      <option value="auto">Auto-detect</option>
                      <option value="es">Spanish (es)</option>
                      <option value="fr">French (fr)</option>
                      <option value="de">German (de)</option>
                    </select>
                  </div>
                  <div className="flex items-center gap-2 pt-5">
                    <input
                      type="checkbox"
                      id="vad_toggle"
                      checked={settings.vad_filter}
                      onChange={(e) => setSettings({ ...settings, vad_filter: e.target.checked })}
                      className="rounded accent-primary w-4 h-4 cursor-pointer"
                    />
                    <label
                      htmlFor="vad_toggle"
                      className="text-xs font-medium text-text-secondary cursor-pointer"
                    >
                      VAD Noise Filter
                    </label>
                  </div>
                </div>

                {/* Save Button */}
                <button
                  type="submit"
                  className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-primary hover:bg-primary-hover text-white font-medium text-xs transition-colors shadow-sm"
                >
                  <Save className="w-4 h-4" />
                  Save Voice Settings
                </button>

                {settingsSavedToast && (
                  <p className="text-center text-xs text-emerald-400 font-medium">
                    ✓ Settings saved successfully
                  </p>
                )}
              </form>
            </div>
          ) : (
            /* Interaction History Panel */
            <div className="p-6 rounded-2xl bg-surface border border-border shadow-lg flex flex-col h-full min-h-[420px]">
              <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-primary" />
                  <h3 className="text-sm font-bold text-text-primary">Voice Dialogue History</h3>
                </div>
                <span className="text-xs text-text-secondary font-mono">
                  {history.length} {history.length === 1 ? 'turn' : 'turns'}
                </span>
              </div>

              {history.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-text-secondary space-y-2">
                  <AudioWaveform className="w-10 h-10 opacity-30 text-primary" />
                  <p className="text-xs">No voice interactions yet.</p>
                  <p className="text-[11px] opacity-70">
                    Tap the microphone button or say "{settings.wake_word}" to begin.
                  </p>
                </div>
              ) : (
                <div className="flex-1 overflow-y-auto space-y-3.5 pr-1 max-h-[380px]">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="p-3.5 rounded-xl bg-surface-subtle border border-border space-y-2 text-xs"
                    >
                      <div className="flex items-center justify-between text-[11px] text-text-secondary">
                        <span className="font-semibold text-text-primary">User</span>
                        <span>
                          {item.timestamp} • {Math.round(item.duration_ms)}ms
                        </span>
                      </div>
                      <p className="text-text-secondary italic">"{item.transcript}"</p>
                      <div className="pt-2 border-t border-border/50">
                        <span className="font-semibold text-primary block mb-1">
                          {settings.assistant_name}
                        </span>
                        <p className="text-text-primary">{item.text_response}</p>
                      </div>
                      {item.audio_url && (
                        <div className="flex items-center gap-2 pt-1">
                          <button
                            onClick={() => playAudio(item.audio_url!, item.id)}
                            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                              activeAudioPlaying === item.id
                                ? 'bg-primary text-white'
                                : 'bg-surface hover:bg-border text-text-secondary'
                            }`}
                          >
                            <Play className="w-3 h-3" />
                            {activeAudioPlaying === item.id ? 'Playing...' : 'Replay Voice'}
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
