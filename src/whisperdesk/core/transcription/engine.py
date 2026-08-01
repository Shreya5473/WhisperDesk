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
        """
        model_size: tiny, base, small, medium, large-v3 — bigger = more
                    accurate but slower. 'base' is a good dev default.
        device:     'cpu' or 'cuda' (if you have an NVIDIA GPU).
        compute_type: 'int8' quantizes the model to run faster on CPU
                      with a small accuracy tradeoff. Use 'float16' on GPU.
        """
        # Model loading is slow (reads weights from disk into memory) —
        # we do it ONCE here, not per-transcription, and reuse the
        # instance. This is why TranscriptionEngine is a class, not
        # just a function: it holds expensive state.
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe a numpy float32 audio array into text."""
        if audio.size == 0:
            return ""

        segments, info = self.model.transcribe(
            audio,
            language=None,   # None = auto-detect language
            vad_filter=True, # skips silent portions — faster + cleaner output
        )

        # segments is a generator — Whisper yields text in chunks as it
        # processes the audio, rather than returning one giant string.
        # We join them into the final transcript here.
        text_parts = [segment.text.strip() for segment in segments]
        return " ".join(text_parts).strip()