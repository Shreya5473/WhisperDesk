"""
Audio recording using a streaming callback approach.
...
"""

import queue
import numpy as np
import sounddevice as sd


class AudioRecorder:
    """Records microphone audio into memory using a background stream."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels

        self._audio_queue: queue.Queue = queue.Queue()
        self._stream: sd.InputStream | None = None
        self._is_recording = False

        # Optional callback fired with a 0.0-1.0 "how loud is this
        # chunk" value on every audio callback. The GUI uses this to
        # drive the live waveform animation.
        self.on_level: callable | None = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[AudioRecorder] status warning: {status}")
        self._audio_queue.put(indata.copy())

        if self.on_level:
            # RMS (root-mean-square) is the standard way to measure
            # perceived loudness of an audio chunk -- square each
            # sample, average, square root. Louder speech = higher
            # RMS. We scale it up since raw mic RMS values are tiny.
            rms = float(np.sqrt(np.mean(indata**2)))
            level = min(1.0, rms * 8)  # scale factor tuned by feel
            self.on_level(level)

    def start(self) -> None:
        if self._is_recording:
            return
        self._audio_queue = queue.Queue()
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()
        self._is_recording = True

    def stop(self) -> np.ndarray:
        if not self._is_recording:
            return np.array([], dtype="float32")
        self._stream.stop()
        self._stream.close()
        self._is_recording = False

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