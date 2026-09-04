import pytest
from backend.app.services.voice.wake_word.factory import wake_word_factory
from backend.app.services.voice.wake_word.openwakeword_detector import OpenWakeWordDetector
from backend.app.services.voice.wake_word.porcupine_detector import PorcupineDetector
from backend.app.services.voice.wake_word.mock_detector import MockWakeWordDetector

def test_wake_word_detector_factory():
    detector = wake_word_factory.get_detector("mock")
    assert detector is not None
    assert detector.detector_name == "mock"

    oww = wake_word_factory.get_detector("openwakeword")
    assert oww is not None
    assert oww.detector_name == "openwakeword"

    porc = wake_word_factory.get_detector("porcupine")
    assert porc is not None
    assert porc.detector_name == "porcupine"

def test_wake_word_configuration():
    detector = MockWakeWordDetector(wake_word="Hey Max")
    assert detector.get_wake_word() == "Hey Max"

    detector.set_wake_word("Hey Aether")
    assert detector.get_wake_word() == "Hey Aether"

def test_mock_wake_word_detection():
    detector = MockWakeWordDetector(wake_word="Hey Max")
    dummy_chunk = b"\x00" * 3200
    # Before trigger
    assert detector.detect(dummy_chunk) is False

    # Trigger next
    detector.trigger_next()
    assert detector.detect(dummy_chunk) is True
    # Should consume the trigger
    assert detector.detect(dummy_chunk) is False

def test_openwakeword_detector_availability():
    oww = OpenWakeWordDetector(wake_word="alexa")
    assert oww.is_available() is True
    assert oww.get_wake_word() == "alexa"
    # Testing silence chunk does not trigger
    dummy_chunk = b"\x00" * 3200
    assert oww.detect(dummy_chunk) is False
