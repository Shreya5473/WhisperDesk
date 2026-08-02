"""
Local speech-to-text transcription using faster-whisper.

faster-whisper is a CTranslate2 reimplementation of OpenAI's Whisper —
same model weights, significantly faster and lighter on CPU/RAM than
the original PyTorch implementation.
"""

import numpy as np
from faster_whisper import WhisperModel


class TranscriptionEngine:
    """Wraps a local Whisper model for converting audio arrays to text."""

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe a numpy float32 audio array into text."""
        if audio.size == 0:
            return ""

        segments, info = self.model.transcribe(
            audio,
            language="en",
            vad_filter=True,
        )
        

        # segments is a generator — Whisper yields text in chunks as it
        # processes the audio, rather than returning one giant string.
        # We join them into the final transcript here.
        text_parts = [segment.text.strip() for segment in segments]
        return " ".join(text_parts).strip()