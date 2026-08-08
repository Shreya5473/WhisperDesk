# WhisperDesk

![CI](https://github.com/Shreya5473/WhisperDesk/actions/workflows/ci.yml/badge.svg)

**A local-first, bilingual, privacy-focused voice-to-text desktop app for macOS — with a full Retrieval-Augmented Generation (RAG) pipeline that lets you ask spoken questions about your own notes and get grounded, spoken-style answers back.**

Built from scratch as a deeper, more feature-rich alternative: entirely local transcription and translation (no cloud dependency for either), a genuine end-to-end RAG system rather than a thin API wrapper, a custom-built animated GUI, persistent user settings, automated tests, and CI — all developed and debugged from the ground up.

---

## Table of Contents

- [Why This Project Exists](#why-this-project-exists)
- [Features, in Depth](#features-in-depth)
  - [Bilingual Dictation (English + Arabic)](#bilingual-dictation-english--arabic)
  - [Voice-Activated RAG](#voice-activated-rag)
  - [Snippet Expansion](#snippet-expansion)
  - [Live Recording Overlay](#live-recording-overlay)
  - [Persistent History](#persistent-history)
  - [Configurable Settings](#configurable-settings)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Design Patterns Used](#design-patterns-used)
- [How Dictation Works, Step by Step](#how-dictation-works-step-by-step)
- [How Voice RAG Works, Step by Step](#how-voice-rag-works-step-by-step)
- [Setup](#setup)
- [macOS Permissions](#macos-permissions)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Continuous Integration](#continuous-integration)
- [Development Journey & Lessons Learned](#development-journey--lessons-learned)
- [Roadmap](#roadmap)
- [License](#license)

---

## Why This Project Exists

Most dictation tools either send your voice to the cloud (privacy tradeoff) or only do the bare minimum: speech-to-text and nothing else. WhisperDesk was built to explore what a *complete*, locally-run voice assistant for personal notes could look like — one where:

- Your voice never leaves your machine for transcription or translation
- The app doesn't just transcribe, it also **understands** your notes well enough to answer questions about them
- Every architectural decision is deliberate and explainable — not just "call an API and glue the output together"

This project touches genuinely hard, real-world engineering problems: multithreaded audio streaming, thread-safe GUI updates, local ML inference, vector search, prompt design for grounded LLM answers, and macOS-specific systems programming (global hotkeys, simulated keystrokes, Accessibility permissions) — all built and debugged first-hand.

## Features, in Depth

### Bilingual Dictation (English + Arabic)

This is one of WhisperDesk's core differentiators: **every single dictation is bilingual by default.**

When you hold the dictation hotkey and speak, two things happen in sequence:

1. **Transcription** — [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (a fast, local reimplementation of OpenAI's Whisper model, running via CTranslate2) converts your speech into English text, entirely on-device.
2. **Translation** — that English text is immediately passed to [Argos Translate](https://github.com/argosopentech/argos-translate), an offline machine translation engine, which translates it into Arabic (or any other language pair you configure in Settings — Spanish, French, and Hindi are also supported out of the box, and more language pairs can be added).

**Both versions are kept:**
- The **English version** is what gets typed into your focused app (e.g. Notes, Slack, an email) — since that's typically what you're actively writing in.
- **Both the English and Arabic versions** are saved to your local history database, so you always have a bilingual record of everything you've dictated.

This is a genuine two-stage AI pipeline — a speech recognition model followed by a separate machine translation model — not a single model doing both jobs. It mirrors how many real-world live-captioning and dubbing systems are architected: transcribe first, translate the transcript second, because Whisper's own built-in translation mode only supports *any language → English*, never the reverse or between two non-English languages.

Translation can be toggled on/off, and the target language changed, from the Settings window at any time (takes effect on next app restart).

### Voice-Activated RAG

Hold `Cmd+Shift+A`, ask a question out loud about your own notes, and get a spoken-style answer — grounded in what you actually wrote, not the LLM's general training knowledge.

The full pipeline, in order:

1. **Chunking** — long documents are split into overlapping ~500-character chunks at sentence boundaries, so each chunk represents one coherent idea (see `core/rag/chunker.py`)
2. **Embedding** — each chunk is converted into a 384-dimensional vector using a local `sentence-transformers` model (`all-MiniLM-L6-v2`), capturing semantic meaning rather than exact wording
3. **Storage** — vectors are stored in a local, persistent [ChromaDB](https://www.trychroma.com/) database, with deterministic content-hashed IDs so re-ingesting the same document never creates duplicates
4. **Retrieval** — when you ask a question, it's embedded the same way, and ChromaDB finds the most semantically similar stored chunks — this is meaning-based search, so "How does the app store data?" correctly retrieves a chunk about "SQLite" and "Repository pattern" even without any shared keywords
5. **Generation** — the question plus the retrieved chunks are sent to Groq's `llama-3.3-70b-versatile` model with an explicit system prompt instructing it to answer *only* from the provided excerpts, and to say so honestly if it can't — this is what makes the answer **grounded** rather than hallucinated

The answer is both typed into your focused app and briefly shown in the recording overlay.

### Snippet Expansion

Define short trigger words that automatically expand into longer text during dictation — e.g. saying "eml" expands to your actual email address. Matching is whole-word only (via regex word boundaries, so "eml" won't wrongly match inside "enamel") and case-insensitive by default. Snippets are stored in SQLite and persist across restarts.

### Live Recording Overlay

A custom-built, frameless, always-on-top floating pill window (built with PyQt6, hand-drawn with `QPainter` — not a generic OS dialog) appears at the bottom of your screen while you're dictating or asking a question. It shows:
- A pulsing recording indicator
- A live animated waveform of 9 bars that grow and shrink in real time based on your actual microphone volume (computed via RMS — root-mean-square — audio level metering)
- A status label ("Listening...", "Transcribing...", "Thinking...")

The overlay never steals keyboard focus from whatever app you're dictating into, and safely receives updates from background audio/hotkey threads via Qt's signal/slot system.

### Persistent History

Every dictation — English text, Arabic translation, timestamp, and word count — is saved to a local SQLite database (`~/.whisperdesk/whisperdesk.db`), accessed exclusively through a `HistoryRepository` class using parameterized queries (no raw SQL string interpolation, protecting against SQL injection).

### Configurable Settings

A dedicated Settings window (opened from the menu bar tray icon) lets you change:
- Both hotkey combinations
- Whisper model size (tiny/base/small/medium — trade-off between speed and accuracy)
- Whether translation is enabled, and which language it targets

Settings persist as JSON at `~/.whisperdesk/settings.json`, with automatic fallback to sensible defaults for any setting missing from an older config file (so future app updates that add new settings never break existing installs).

## Architecture

![WhisperDesk architecture diagram](docs/architecture.svg)

The app is built with a strict **layered architecture**: all business logic lives in `core/`, completely decoupled from the GUI. Every core feature — audio recording, transcription, translation, the entire RAG pipeline — can be run and tested headlessly via the `test_*.py` scripts in the project root, with zero dependency on PyQt6 or the GUI ever being involved. The GUI (`frontend/`) is a thin layer that only wires signals from `core/` components to visual updates.

Two hotkeys trigger two different pipelines that share the same underlying `AudioRecorder` and `TranscriptionEngine`:
- **Dictation** (`Cmd+Shift+Space`): record → transcribe → expand snippets → translate → save to history → inject text
- **Voice RAG** (`Cmd+Shift+A`): record → transcribe → retrieve relevant notes → generate grounded answer → inject answer

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Speech-to-text | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Local, CTranslate2-accelerated Whisper — ~4x faster than the original PyTorch implementation, no cloud dependency |
| Translation | [Argos Translate](https://github.com/argosopentech/argos-translate) | Fully offline machine translation, keeping the entire pipeline privacy-focused |
| Embeddings | [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) | Small, fast, local semantic embedding model |
| Vector search | [ChromaDB](https://www.trychroma.com/) | Persistent, file-based vector database — no server process required |
| Answer generation | [Groq](https://groq.com/) (`llama-3.3-70b-versatile`) | Free tier, very fast inference for the one component that does require an external API |
| GUI | PyQt6 | Native-feeling macOS desktop UI, custom-drawn overlay and system tray integration |
| Storage | SQLite | Serverless, file-based, perfect fit for a single-user desktop app |
| Hotkeys / input simulation | [pynput](https://pynput.readthedocs.io/) | Global hotkey listening and simulated keyboard text injection |
| Testing | pytest | Unit tests for all pure-logic components |
| CI | GitHub Actions | Automated test runs on every push |

## Project Structure

```
whisperdesk/
├── .github/workflows/ci.yml     # GitHub Actions test pipeline
├── docs/
│   └── architecture.svg          # Architecture diagram
├── src/whisperdesk/
│   ├── core/
│   │   ├── audio/
│   │   │   └── recorder.py       # Streaming mic capture, thread-safe queue, RMS level metering
│   │   ├── transcription/
│   │   │   └── engine.py         # faster-whisper wrapper
│   │   ├── translation/
│   │   │   └── translator.py     # Argos Translate wrapper (offline, bilingual)
│   │   ├── snippets/
│   │   │   └── expander.py       # Regex-based trigger-word expansion
│   │   ├── settings/
│   │   │   └── settings_manager.py  # JSON-backed persistent settings with default fallback
│   │   └── rag/
│   │       ├── chunker.py        # Overlapping, boundary-aware document chunking
│   │       ├── embeddings.py     # Local sentence-transformer embedding wrapper
│   │       ├── vector_store.py   # ChromaDB persistent vector storage + search
│   │       ├── ingestion.py      # Chunk -> embed -> store pipeline, deduplicated via hashed IDs
│   │       ├── retriever.py      # Semantic search over stored notes
│   │       ├── generator.py      # Groq LLM call with grounded-answer system prompt
│   │       └── pipeline.py       # Facade combining ingestion + retrieval + generation
│   ├── storage/
│   │   ├── db.py                 # SQLite connection + schema setup
│   │   ├── history_repository.py # All dictation-history SQL, parameterized queries
│   │   └── snippet_repository.py # All snippet SQL
│   ├── hotkeys/
│   │   └── manager.py            # Global hotkey press/release detection (pynput)
│   ├── injection/
│   │   └── text_injector.py      # Simulated keyboard text injection
│   └── frontend/
│       ├── recording_overlay.py  # Custom PyQt6 floating overlay + animated waveform
│       ├── settings_window.py    # Settings GUI
│       └── controller.py         # Bridges background threads to GUI via Qt signals
├── tests/                        # pytest unit tests
├── main.py                       # App entry point: Qt event loop, tray icon, signal wiring
├── requirements.txt
└── README.md
```

## Design Patterns Used

- **Repository pattern** — all SQL access for history and snippets lives in dedicated repository classes (`HistoryRepository`, `SnippetRepository`); nothing else in the app touches raw SQL, making it trivial to swap SQLite for another database later without touching calling code.
- **Facade pattern** — `RAGPipeline` hides five separate collaborating components (embedder, vector store, ingester, retriever, generator) behind two simple methods: `add_notes()` and `ask()`.
- **Signal/slot (Observer) pattern** — Qt's signal/slot system safely bridges events from background threads (microphone callbacks, hotkey listeners) into main-thread-safe GUI updates, without ever touching a widget from a non-main thread.
- **Dependency injection (light)** — components like `Retriever` and `DocumentIngester` receive their `EmbeddingModel` and `VectorStore` instances via constructor arguments rather than creating them internally, making each piece independently testable.
- **Deterministic ID hashing** — vector store chunk IDs are generated via `sha256(source_name + chunk_index)`, so re-ingesting an unchanged document is idempotent (no duplicate chunks) — an important, easy-to-miss detail in real RAG systems.

## How Dictation Works, Step by Step

1. User holds `Cmd+Shift+Space` anywhere on macOS.
2. `HotkeyManager` (running on a background thread via `pynput`) detects the combo and calls back into `AppController`.
3. `AudioRecorder.start()` opens a streaming microphone input; each audio chunk is pushed into a thread-safe `Queue` and its RMS volume is emitted as a Qt signal, animating the overlay's waveform live.
4. On release, `AudioRecorder.stop()` concatenates all buffered audio into one array.
5. `TranscriptionEngine` (faster-whisper) transcribes it to English text.
6. `SnippetExpander` expands any matching trigger words.
7. If translation is enabled, `Translator` (Argos Translate) produces the Arabic (or configured language) version.
8. Both versions are saved via `HistoryRepository`.
9. The English text is typed into whatever app currently has focus via `TextInjector`.

## How Voice RAG Works, Step by Step

1. Notes are ingested ahead of time via `RAGPipeline.add_notes(text)` — chunked, embedded, and stored in ChromaDB.
2. User holds `Cmd+Shift+A` and asks a question out loud.
3. The same `AudioRecorder` → `TranscriptionEngine` path transcribes the spoken question to text.
4. `Retriever` embeds the question and searches the vector store for the most semantically relevant stored chunks.
5. `AnswerGenerator` sends the question and retrieved chunks to Groq's LLM, with a system prompt enforcing that it only answers from the provided context.
6. The generated answer is injected as text into the focused app and briefly shown in the overlay.

## Setup

**Requirements:** macOS, Python 3.11+ (developed and tested on 3.14), a free [Groq API key](https://console.groq.com/)

```bash
git clone https://github.com/Shreya5473/WhisperDesk.git
cd WhisperDesk

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
```

The first run will download the Whisper model, the Argos Translate language pack, and the sentence-transformer embedding model — all cached locally afterward, no repeated downloads.

### Run

```bash
python main.py
```

A red icon appears in your macOS menu bar. From there, open **Settings** to configure hotkeys and languages, or **Quit WhisperDesk** to exit.

## macOS Permissions

WhisperDesk needs two macOS permission grants:

| Permission | Why | Where to grant it |
|---|---|---|
| Microphone | Recording your voice | System Settings → Privacy & Security → Microphone |
| Accessibility | Global hotkey detection + simulated text typing | System Settings → Privacy & Security → Accessibility |

> **Development note:** these permissions are tied to the exact running process. If you're developing/running from an IDE's integrated terminal, permission grants may not reliably apply until that IDE is fully quit and reopened. Running from a plain macOS Terminal window tends to be more reliable during development.

## Configuration

All settings are editable via the tray icon → Settings window, or directly at `~/.whisperdesk/settings.json`:

```json
{
  "dictate_hotkey": "<cmd>+<shift>+<space>",
  "query_hotkey": "<cmd>+<shift>+a",
  "whisper_model_size": "base",
  "translation_target_language": "ar",
  "translation_enabled": true
}
```

Changes take effect on the next app restart.

## Running Tests

```bash
python -m pytest tests/ -v
```

17 unit tests cover the document chunker (including a regression test for an infinite-loop edge case found during development), snippet expander, settings persistence, and SQLite history repository — all using in-memory databases and temporary file paths, so tests never touch real user data.

## Continuous Integration

Every push to `main` automatically runs the full test suite via GitHub Actions (`.github/workflows/ci.yml`), on a fresh macOS runner. See the badge at the top of this README for current status.

## Development Journey & Lessons Learned

This project was built incrementally, phase by phase, with each core piece tested standalone before integration:

1. Streaming audio capture with a thread-safe producer/consumer queue
2. Local Whisper transcription, then offline bilingual translation
3. SQLite persistence via the Repository pattern
4. Regex-based snippet expansion
5. Global hotkeys and simulated text injection (including real debugging of macOS Accessibility permission quirks and reserved-shortcut collisions like `Cmd+Shift+Q` triggering macOS's own logout dialog)
6. A custom PyQt6 GUI overlay with live waveform animation, including tracking down a genuine macOS-specific window-compositing bug
7. A full RAG pipeline built and tested stage by stage: chunking (including fixing a real infinite-loop bug in boundary detection), local embeddings, ChromaDB vector search, and grounded LLM generation — including debugging stale/contaminated vector store data, a real production RAG failure mode
8. A persistent, JSON-backed settings system with safe default-fallback for forward compatibility
9. Unit tests and a working CI pipeline, including fixing a Python-version mismatch between local development and the CI environment
10. Documentation and architecture polish

## Roadmap

- [ ] In-app history browser UI (currently viewable only via direct SQLite access)
- [ ] Packaged, distributable `.app` build
- [ ] Live-updating settings without requiring an app restart
- [ ] Additional source languages beyond English dictation

## License

MIT