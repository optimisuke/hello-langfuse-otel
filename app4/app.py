import base64
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
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
    # disable_batch=True to flush immediately in short-lived containers
    Traceloop.init(
        app_name=os.getenv("APP_NAME", "app3-openllmetry"),
        disable_batch=True,
        api_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
        headers={"Authorization": f"Basic {auth}"},
    )
    print("Traceloop initialized (OpenLLMetry OTEL export).")


def run_chat() -> None:
    client = OpenAI()
    resp = client.chat.completions.create(
        messages=[{"role": "user", "content": "LLM Observabilityって何？"}],
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
    print(resp)


def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set.")
        sys.exit(1)

    setup_traceloop()
    run_chat()


if __name__ == "__main__":
    main()
