# FastAPI + Firestore サンプル

このリポジトリは、FastAPI を使って Firestore（またはエミュレータ）に接続するシンプルな REST API のサンプルです。

概要
- API:
	- POST /upsert_visited  - JSON body: {"visitor_id": "<uuid>", "day": "first"|"second", "visited": true}
	- POST /read_visitor    - JSON body: {"visitor_id": "<uuid>"}
	- GET  /health

ローカルでの実行（エミュレータをホストで動かす場合）

1. 前提
	- Docker がインストールされていること
	- （推奨）gcloud SDK がインストールされていること（Firestore エミュレータを使う場合）

2. ホストで Firestore エミュレータを起動する例

```bash
# 1回だけセットアップ（もしまだなら）
# gcloud components install cloud-firestore-emulator

# エミュレータを 0.0.0.0:8923 で起動（ホスト上で他のプロセスからアクセス可能にする）
gcloud emulators firestore start --host-port=0.0.0.0:8923
```

3. backend コンテナを起動（コンテナからホストのエミュレータに接続する設定を含む）

```bash
# コンテナ側で環境変数 FIRESTORE_EMULATOR_HOST を設定し、
# host.docker.internal をコンテナから解決させるために host-gateway を追加します
docker build -t kouyousai-backend:local ./backend
docker run -d \
	--name kouyousai-backend-local \
	--add-host=host.docker.internal:host-gateway \
	-e PORT=8000 \
	-e FIRESTORE_EMULATOR_HOST=host.docker.internal:8923 \
	-e FIRESTORE_PROJECT_ID=demo-project \
	-p 8000:8000 \
	kouyousai-backend:local
```

4. API のテスト例

```bash
# ヘルスチェック
curl http://localhost:8000/health

# upsert (first day を true にする例)
curl -X POST http://localhost:8000/upsert_visited \
	-H 'Content-Type: application/json' \
	-d '{"visitor_id":"c357eafd-00a8-4243-8ec5-270d185edd1e","day":"first","visited":true}'

# read
curl -X POST http://localhost:8000/read_visitor \
	-H 'Content-Type: application/json' \
	-d '{"visitor_id":"c357eafd-00a8-4243-8ec5-270d185edd1e"}'
```
