import time
from src.whisperdesk.core.audio.recorder import AudioRecorder

recorder = AudioRecorder()
print("Recording for 3 seconds... speak now!")
recorder.start()
time.sleep(3)
audio = recorder.stop()

print(f"Captured {len(audio)} samples ({len(audio) / recorder.sample_rate:.2f} seconds)")