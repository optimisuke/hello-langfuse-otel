# hello-langfuse-otel

LangChain + OpenAI だけで動く最小チャットデモです（Langfuse/Traceloop のコードは削除済み）。

## 前提
- Python 3.10+ 推奨
- OpenAI 互換の API キー (`OPENAI_API_KEY`)

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
docker compose run --rm app
```
`stdin_open: true` と `tty: true` を設定しているので、対話的にチャットできます。終了時は `exit` / `quit`。  
サービスを立ち上げっぱなしにしたい場合は `docker compose up --build -d app` で起動し、`docker compose exec -it app /bin/sh` → `python app.py` で対話できます。

## メモ
- デフォルトモデルは `gpt-4o-mini`。`OPENAI_MODEL` で上書きできます。
- 会話履歴は LangChain のメッセージオブジェクトでメモリ保持し、文脈を維持します。
