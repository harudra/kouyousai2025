from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import firestore
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

FIRESTORE_PROJECT_ID = os.environ.get("FIRESTORE_PROJECT_ID", "demo-project")
logger.info("Firestore Project ID: %s", FIRESTORE_PROJECT_ID)

FIRESTORE_COLLECTION_NAME = os.environ.get("FIRESTORE_COLLECTION", "visitors")
logger.info("Firestore Collection Name: %s", FIRESTORE_COLLECTION_NAME)

logger.info("FirestoreクライアントをプロジェクトID=%sでグローバルに初期化中", FIRESTORE_PROJECT_ID)
firestore_client = firestore.Client(project=FIRESTORE_PROJECT_ID)
logger.debug("Firestoreクライアントがグローバルに初期化されました。")


class Visitor(BaseModel):
    name: str
    email: str


@app.post("/visitor")
async def create_visitor(visitor: Visitor):
    try:
        doc_ref = firestore_client.collection(
            FIRESTORE_COLLECTION_NAME).document()
        visitor_data = visitor.model_dump()

        visitor_data["created_at"] = firestore.SERVER_TIMESTAMP

        doc_ref.set(visitor_data)
        logger.info("アイテム %s (ID=%s) を作成しました。", visitor_data, doc_ref.id)

        return {"id": doc_ref.id, **visitor_data}
    except Exception as e:
        logger.exception("アイテムの作成に失敗しました: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visitor/{visitor_id}")
async def read_visitor(visitor_id: str):
    try:
        doc = firestore_client.collection(
            FIRESTORE_COLLECTION_NAME).document(visitor_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="アイテムが見つかりません")
        return doc.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("アイテム %s の読み取りに失敗しました: %s", visitor_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
