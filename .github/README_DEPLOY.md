GitHub Actions: Cloud Run デプロイワークフロー

ファイル: `.github/workflows/deploy-cloud-run.yml`
必須のリポジトリシークレット（GitHub リポジトリ → Settings → Secrets and variables → Actions）:
- `GCLOUD_AUTH`：サービスアカウントの JSON キー（下の「最小権限」を参照）
- `GCP_PROJECT_ID`：GCP プロジェクト ID
- `SERVICE_NAME`：Cloud Run のサービス名
- `GCP_IMAGE`：イメージ名（例: kouyousai-backend）
- `GCP_REGION`：デプロイ先リージョン（例: asia-northeast1）
ワークフローを `backend/Dockerfile` を使うようにする方法

`backend` フォルダ内の `Dockerfile`（`backend/Dockerfile`）を使い、コンテキストを `./backend` に限定してビルドするには、次を実行してください:

```yaml
# Build（backend/Dockerfile を使い backend をコンテキストにする）
docker build --platform linux/amd64 -f backend/Dockerfile -t asia-northeast1-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$IMAGE:$TAG ./backend

# Push
docker push asia-northeast1-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$IMAGE:$TAG
```

GitHub シークレットの登録手順
1. GitHub リポジトリに移動し、`Settings` → `Secrets and variables` → `Actions` を開きます。
2. `New repository secret` をクリックします。
3. `Name` に `GCLOUD_AUTH` を入力し、`Value` に `key.json` の全文を貼り付けて保存します。
4. 同様に文字列型のシークレット `GCP_PROJECT_ID`、`SERVICE_NAME`、`GCP_IMAGE`、`GCP_REGION` を登録します。