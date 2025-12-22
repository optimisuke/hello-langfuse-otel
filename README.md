# hello-langfuse-otel

LangChain + OpenAI だけで動く最小チャットデモです（Langfuse/Traceloop のコードは削除済み）。

## 前提
- Python 3.10+ 推奨
- OpenAI 互換の API キー (`OPENAI_API_KEY`)
- （任意）Langfuse 自前ホストでトレースを見たい場合は `langfuse` サービスを起動し、`LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` を設定

## セットアップ（uv）
```bash
uv venv
source .venv/bin/activate
uv sync
cp .env.example .env  # キーを書き換える
```

## チャット実行（uv）
```bash
uv run python app.py
```
メッセージを入力してください。`exit` または `quit` で終了します。

## Docker Compose で実行
```bash
cp .env.example .env  # キーを書き換える
cp .env.langfuse.example .env.langfuse  # Langfuseを使う場合に書き換える
docker compose up -d langfuse langfuse-db  # Langfuse UI を http://localhost:3000 で起動
docker compose run --rm app               # 対話チャット（Langfuseキーがあればトレース記録）
```
`stdin_open: true` と `tty: true` を設定しているので、対話的にチャットできます。終了時は `exit` / `quit`。  
サービスを立ち上げっぱなしにしたい場合は `docker compose up --build -d app` で起動し、`docker compose exec -it app /bin/sh` → `python app.py` で対話できます。

## メモ
- デフォルトモデルは `gpt-4o-mini`。`OPENAI_MODEL` で上書きできます。
- 会話履歴は LangChain のメッセージオブジェクトでメモリ保持し、文脈を維持します。
- Langfuse に送る場合は Langfuse UI でプロジェクトキー（PUBLIC/SECRET）を作成し、`.env` に `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY`、ホストURLを `LANGFUSE_HOST`（Compose なら `http://langfuse:3000` 推奨）として設定してください。
