import base64
import os
import sys
from operator import itemgetter
from typing import Optional

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_openai import ChatOpenAI
from traceloop.sdk import Traceloop


def configure_otlp_for_langfuse() -> Optional[str]:
    """
    Build OTLP endpoint/headers (Basic Auth) for Langfuse OTEL ingestion.
    Returns auth header value if configured.
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    base_url = os.getenv("LANGFUSE_BASE_URL",
                         "http://localhost:3000").rstrip("/")
    if not public_key or not secret_key:
        print("LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY not set. OTLP export skipped.")
        return None
    auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
    os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT",
                          f"{base_url}/api/public/otel")
    os.environ.setdefault("OTEL_EXPORTER_OTLP_HEADERS",
                          f"Authorization=Basic {auth}")
    return auth


def setup_traceloop() -> None:
    auth = configure_otlp_for_langfuse()
    if not auth:
        print("Tracing skipped: Langfuse OTLP auth not configured.")
        return
    # disable_batch=True to flush immediately in short-lived containers
    app_name = os.getenv("APP_NAME", "app4-openllmetry")
    Traceloop.init(
        app_name=app_name,
        disable_batch=True,
        api_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        headers={"Authorization": f"Basic {auth}"},
    )
    print("Traceloop initialized (OpenLLMetry OTEL export).")


def build_model() -> ChatOpenAI:
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    return ChatOpenAI(model=model_name, temperature=temperature)


def main() -> None:
    load_dotenv()
    setup_traceloop()

    try:
        model = build_model()
    except Exception as exc:
        print(
            f"Could not start ChatOpenAI. Check your OpenAI credentials: {exc}")
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

        config = {"run_name": "app4-two-step"}

        answer = chain2.invoke(
            {"person": person, "language": "日本語"}, config=config)
        print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
