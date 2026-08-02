import time
from src.whisperdesk.core.audio.recorder import AudioRecorder
from src.whisperdesk.core.transcription.engine import TranscriptionEngine
from src.whisperdesk.hotkeys.manager import HotkeyManager
from src.whisperdesk.injection.text_injector import TextInjector

recorder = AudioRecorder()
print("Loading Whisper model...")
engine = TranscriptionEngine(model_size="base")
injector = TextInjector()

def on_hotkey_press():
    print("Hotkey pressed — recording...")
    recorder.start()

def on_hotkey_release():
    print("Hotkey released — transcribing...")
    audio = recorder.stop()
    text = engine.transcribe(audio, sample_rate=recorder.sample_rate)
    print(f"Transcript: {text}")
    injector.inject(text + "\n")

hotkey_manager = HotkeyManager(hotkey="<cmd>+<shift>+<space>")
hotkey_manager.on_activate = on_hotkey_press
hotkey_manager.on_deactivate = on_hotkey_release
hotkey_manager.start()

print("Listening for Cmd+Shift+Space... hold it, speak, release. Ctrl+C to quit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    hotkey_manager.stop()
    print("\nStopped.")