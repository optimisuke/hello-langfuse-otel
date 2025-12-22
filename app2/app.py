import os
import sys
from operator import itemgetter
from typing import Optional

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
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


def build_model() -> ChatOpenAI:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    return ChatOpenAI(model=model_name, temperature=temperature)


def main() -> None:
    load_dotenv()
    langfuse_handler = build_langfuse_handler()

    try:
        model = build_model()
    except Exception as exc:
        print(f"Could not start ChatOpenAI. Check your OpenAI credentials: {exc}")
        sys.exit(1)

    # チェーンを組んで、invoke時に callbacks をまとめて渡す
    prompt1 = ChatPromptTemplate.from_template("{person} はどの都市の出身？")
    prompt2 = ChatPromptTemplate.from_template(
        "その都市 {city} はどの国？回答は {language} で簡潔に。"
    )
    chain1 = prompt1 | model | StrOutputParser()
    chain2 = (
        {"city": chain1, "language": itemgetter("language")}
        | prompt2
        | model
        | StrOutputParser()
    )

    print("Type 'exit' or 'quit' to stop.")
    while True:
        try:
            person = input("Person: ").strip()
            if person.lower() in {"exit", "quit"}:
                break
        except (EOFError, KeyboardInterrupt):
            print("\nStopping chat.")
            break

        config = {"run_name": "chain2-two-step"}
        if langfuse_handler:
            # Langfuse のコールバックをチェーン全体に適用
            config["callbacks"] = [langfuse_handler]

        answer = chain2.invoke({"person": person, "language": "日本語"}, config=config)
        print(f"Answer: {answer}")

    # Langfuse 送信を待たずに終了するのを防ぐためflush
    if langfuse_handler:
        langfuse_handler.flush()


if __name__ == "__main__":
    main()
