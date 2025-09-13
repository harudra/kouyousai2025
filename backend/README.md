# FastAPI + Firestore Emulator サンプル

このリポジトリは、ローカルの Firestore エミュレータに接続する FastAPI REST API のサンプルです。

概要
- API:
	- POST /items  - JSON body: {"name": "foo", "value": 123}
	- GET /items/{id}
	- GET /health

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

# 作成
curl -X POST http://localhost:8000/items \
	-H 'Content-Type: application/json' \
	-d '{"name":"test","value":10}'

# 取得
curl http://localhost:8000/items/<id>
```

Cloud Run にデプロイする場合（概要）

1. 環境の注意
	 - 本番では Firestore のエミュレータを使わず、Google Cloud の本番サービスを使います。
	 - Cloud Run で動かす場合は、コンテナ起動時に `FIRESTORE_EMULATOR_HOST` を設定しないでください。
	 - Cloud Run のサービスアカウントに Firestore へアクセスする権限（roles/datastore.user など）を付与してください。

2. イメージのビルドと gcr への push（例）

```bash
# ビルド
docker build -t gcr.io/<PROJECT_ID>/kouyousai-backend:latest ./backend
# push
docker push gcr.io/<PROJECT_ID>/kouyousai-backend:latest
```

3. Cloud Run デプロイ（例）

```bash
gcloud run deploy kouyousai-backend \
	--image gcr.io/<PROJECT_ID>/kouyousai-backend:latest \
	--platform managed \
	--region us-central1 \
	--allow-unauthenticated \
	--set-env-vars FIRESTORE_PROJECT_ID=<PROJECT_ID>
```

