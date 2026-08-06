from src.whisperdesk.core.rag.generator import AnswerGenerator

generator = AnswerGenerator()

context_chunks = [
    "The database layer uses SQLite via a Repository pattern, storing transcription history and user-defined snippets.",
    "For the GUI, we chose PyQt6, building a custom floating overlay with a live animated waveform.",
]

question = "What database does the project use?"
print(f"Question: {question}")
answer = generator.generate_answer(question, context_chunks)
print(f"Answer: {answer}")