# hello-langfuse-otel

LangChain + OpenAI + Langfuse のチャットデモ。app1/app2/app3/app4 の4サービス構成（各フォルダに分割）。

## ディレクトリ
- `app1/`: Pythonチャット（Composeサービス `app1`）
- `app2/`: もう一つのバリアント（Composeサービス `app2`）
- `app3/`: Traceloop(OpenLLMetry) + OpenAI（素のchat API）で Langfuse OTEL ingest へ送信
- `app4/`: Traceloop(OpenLLMetry) + LangChain チェーン（2段プロンプト）で Langfuse OTEL ingest へ送信

## セットアップ（例：app1をローカルでuv実行）
```bash
cd app1
uv venv && source .venv/bin/activate
uv sync
cp .env.example .env  # キーを書き換える
uv run python app.py
```

## Docker Compose で実行
```bash
cd app1 && cp .env.example .env        # app1のキー
cd ../app2 && cp .env.example .env     # app2のキー
cd ../app3 && cp .env.example .env     # app3のキー（OpenAI + Langfuseキー必須）
cd ../app4 && cp .env.example .env     # app4のキー（OpenAI + Langfuseキー必須）
cd ..
docker compose up -d clickhouse minio redis postgres langfuse-worker langfuse-web
docker compose run --rm app1  # app1チャット
docker compose run --rm app2  # app2チャット
docker compose run --rm app3  # app3: Traceloop(OpenLLMetry)→Langfuse OTEL送信のみ
docker compose run --rm app4  # app4: LangChainチェーンをTraceloop(OpenLLMetry)でOTEL送信
```
`stdin_open: true` と `tty: true` なので対話できます。終了時は `exit` / `quit`。

## Langfuse
- Langfuse UI: http://localhost:3000
- プロジェクトキー（PUBLIC/SECRET）を作成し、各 `.env` に `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` と `LANGFUSE_HOST=http://langfuse-web:3000` を設定。
- app3/4 は Traceloop(OpenLLMetry) で OTEL を Langfuse に送るサンプル。必要なのは `OPENAI_API_KEY` と Langfuseの公開/秘密キーおよび `LANGFUSE_BASE_URL`（ローカル実行は `http://localhost:3000`、Composeは `docker-compose.yml` で `http://langfuse-web:3000` に上書き）だけで、`TRACELOOP_API_KEY` や `APP_NAME` は不要。

## メモ
- デフォルトモデルは `gpt-4o-mini` (`OPENAI_MODEL` で変更)。
- 会話履歴は LangChain のメッセージオブジェクトで保持。
