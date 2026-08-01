"""
Audio recording using a streaming callback approach.

Instead of recording a fixed-length clip, we continuously capture
small chunks of audio into a buffer, and let the caller decide
when to start/stop. This mirrors how real dictation apps work:
you hold a hotkey, speak for as long as you want, release it.
"""

import queue
import numpy as np
import sounddevice as sd


class AudioRecorder:
    """Records microphone audio into memory using a background stream."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        # 16kHz mono is what Whisper expects internally — recording at
        # this rate avoids an extra resampling step later.
        self.sample_rate = sample_rate
        self.channels = channels

        self._audio_queue: queue.Queue = queue.Queue()
        self._stream: sd.InputStream | None = None
        self._is_recording = False

    def _callback(self, indata, frames, time, status):
        """Called automatically by sounddevice on a background thread
        every time a new chunk of audio is available."""
        if status:
            print(f"[AudioRecorder] status warning: {status}")
        # indata is a numpy array — copy it, since sounddevice reuses
        # the same buffer internally on the next callback.
        self._audio_queue.put(indata.copy())

    def start(self) -> None:
        """Begin streaming audio from the microphone."""
        if self._is_recording:
            return  # already recording, ignore duplicate start calls

        self._audio_queue = queue.Queue()  # clear any old data
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()
        self._is_recording = True

    def stop(self) -> np.ndarray:
        """Stop recording and return the full audio as one numpy array."""
        if not self._is_recording:
            return np.array([], dtype="float32")

        self._stream.stop()
        self._stream.close()
        self._is_recording = False

        # Drain the queue into a list of chunks, then stitch into one array
        chunks = []
        while not self._audio_queue.empty():
            chunks.append(self._audio_queue.get())

        if not chunks:
            return np.array([], dtype="float32")

        audio = np.concatenate(chunks, axis=0)
        return audio.flatten()

    @property
    def is_recording(self) -> bool:
        return self._is_recording