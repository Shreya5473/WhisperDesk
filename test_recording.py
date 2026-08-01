import time
from src.whisperdesk.core.audio.recorder import AudioRecorder
from src.whisperdesk.core.transcription.engine import TranscriptionEngine

recorder = AudioRecorder()
print("Loading Whisper model (first run downloads it, be patient)...")
engine = TranscriptionEngine(model_size="base")

print("Recording for 5 seconds... speak now!")
recorder.start()
time.sleep(5)
audio = recorder.stop()

print("Transcribing...")
text = engine.transcribe(audio, sample_rate=recorder.sample_rate)
print(f"Transcript: {text}")