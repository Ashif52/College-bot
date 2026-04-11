# chatbot/cli.py
# ─────────────────────────────────────────────────────────────────────────────
# Interactive CLI for quick testing without running the FastAPI server.
#
# Usage:
#   python -m chatbot.cli
# ─────────────────────────────────────────────────────────────────────────────

import sys
from chatbot import pipeline
from chatbot.config import LLM_PROVIDER, GROQ_MODEL, OPENAI_MODEL


BANNER = """
╔══════════════════════════════════════════════════════════════╗
║         Nexus Institute – Student Enquiry Chatbot           ║
║  Type your question and press Enter. Type 'quit' to exit.    ║
╚══════════════════════════════════════════════════════════════╝
"""

model_name = GROQ_MODEL if LLM_PROVIDER == "groq" else OPENAI_MODEL


def run() -> None:
    print(BANNER)
    print(f"  LLM Provider : {LLM_PROVIDER.upper()}")
    print(f"  Model        : {model_name}")
    print()

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("\nBot: Searching knowledge base...\n")

        try:
            result = pipeline.query(question)
        except Exception as e:
            print(f"[ERROR] {e}\n")
            continue

        print(f"Bot: {result.answer}\n")

        print()


if __name__ == "__main__":
    run()
