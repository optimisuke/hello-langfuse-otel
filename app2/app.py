import os
import sys
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler


def build_langfuse_handler() -> Optional[CallbackHandler]:
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST")

    if not public_key or not secret_key:
        print("Langfuse not configured (set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY).")
        return None

    return CallbackHandler(public_key=public_key, secret_key=secret_key, host=host)


def build_model(langfuse_handler: Optional[CallbackHandler]) -> ChatOpenAI:
    callbacks = [langfuse_handler] if langfuse_handler else None
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        callbacks=callbacks,
    )


def chat_loop(model: ChatOpenAI, langfuse_handler: Optional[CallbackHandler]) -> None:
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

    if langfuse_handler:
        langfuse_handler.flush()


def main() -> None:
    load_dotenv()
    langfuse_handler = build_langfuse_handler()

    try:
        model = build_model(langfuse_handler)
    except Exception as exc:
        print(f"Could not start ChatOpenAI. Check your OpenAI credentials: {exc}")
        sys.exit(1)

    chat_loop(model, langfuse_handler)


if __name__ == "__main__":
    main()
