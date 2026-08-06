"""
Generation: given a question and retrieved context chunks, produce
a grounded answer using an LLM.

This is the "G" in RAG. The key idea: instead of asking the LLM
"what do you know about X" (which risks hallucination from its
general training data), we explicitly hand it the user's own
retrieved notes as context and instruct it to answer ONLY from
that context. This is what makes the answer trustworthy/grounded.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # reads .env and populates environment variables


class AnswerGenerator:
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Make sure you created a .env file "
                "with GROQ_API_KEY=your_key_here"
            )
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        if not context_chunks:
            return "I don't have any notes that seem relevant to that question."

        context = "\n\n".join(
            f"[Excerpt {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)
        )

        # The system prompt is where we enforce "grounded, not
        # hallucinated" -- explicitly instructing the model to only
        # use the provided excerpts, and to say so if it can't
        # answer from them.
        system_prompt = (
            "You are a helpful assistant answering questions using ONLY the "
            "provided excerpts from the user's personal notes. "
            "If the excerpts don't contain enough information to answer, "
            "say so honestly instead of guessing. "
            "Keep answers concise and conversational, since they'll be spoken aloud."
        )

        user_prompt = f"Excerpts from my notes:\n\n{context}\n\nQuestion: {question}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,  # low temperature -- factual/grounded, not creative
        )

        return response.choices[0].message.content