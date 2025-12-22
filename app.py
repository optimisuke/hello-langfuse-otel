import os
import sys
from typing import List

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


def build_model() -> ChatOpenAI:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
    )


def chat_loop(model: ChatOpenAI) -> None:
    messages: List = [
        SystemMessage(
            content="You are a concise assistant in a telemetry demo. Keep responses short and helpful."
        )
    ]

    print("Type 'exit' or 'quit' to stop.")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nStopping chat.")
            break

        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit"}:
            break

        messages.append(HumanMessage(user_text))
        ai_message: AIMessage = model.invoke(messages, config={"run_name": "chat-demo"})
        messages.append(ai_message)
        print(f"Bot: {ai_message.content}")


def main() -> None:
    load_dotenv()
    try:
        model = build_model()
    except Exception as exc:
        print(f"Could not start ChatOpenAI. Check your OpenAI credentials: {exc}")
        sys.exit(1)

    chat_loop(model)


if __name__ == "__main__":
    main()
