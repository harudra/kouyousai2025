from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
from google.cloud import firestore
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 許可するオリジン
    allow_credentials=True,
    allow_methods=["*"],            # GET, POSTなど全許可
    allow_headers=["*"],            # 全ヘッダー許可
)

FIRESTORE_PROJECT_ID = os.environ.get("FIRESTORE_PROJECT_ID", "demo-project")
logger.info("Firestore Project ID: %s", FIRESTORE_PROJECT_ID)

FIRESTORE_COLLECTION_NAME = os.environ.get("FIRESTORE_COLLECTION", "visitors")
logger.info("Firestore Collection Name: %s", FIRESTORE_COLLECTION_NAME)

logger.info("FirestoreクライアントをプロジェクトID=%sでグローバルに初期化中", FIRESTORE_PROJECT_ID)
firestore_client = firestore.Client(project=FIRESTORE_PROJECT_ID)
logger.debug("Firestoreクライアントがグローバルに初期化されました。")


class VisitorByID(BaseModel):
    visitor_id: str


class VisitPayload(BaseModel):
    visitor_id: str
    day: Literal["first", "second"]
    visited: bool


def _serialize_doc(d: dict) -> dict:
    if d is None:
        return {}
    out = {}
    for k, v in d.items():
        if hasattr(v, "isoformat"):
            try:
                out[k] = v.isoformat()
                continue
            except Exception:
                pass
        out[k] = v
    return out


@app.post("/upsert_visited")
async def upsert_visited(payload: VisitPayload):
    """Unified endpoint. Payload: {visitor_id, day: 'first'|'second', visited: bool}"""
    try:
        # day に応じてフィールド名を選択
        if payload.day == "first":
            flag_field = "visited_first_day"
            timestamp_field = "visited_first_day_updated_at"
        elif payload.day == "second":
            flag_field = "visited_second_day"
            timestamp_field = "visited_second_day_updated_at"
        else:
            raise HTTPException(
                status_code=400, detail="day は 'first' または 'second' を指定してください")

        doc_ref = firestore_client.collection(
            FIRESTORE_COLLECTION_NAME).document(payload.visitor_id)

        # 存在確認
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="アイテムが見つかりません")

        # 更新
        data = {flag_field: payload.visited,
                timestamp_field: firestore.SERVER_TIMESTAMP}
        doc_ref.update(data)

        # 保存後のデータを取得
        saved = doc_ref.get()
        saved_data = saved.to_dict() if saved.exists else {}

        # dict化して返す
        resp = {"id": doc_ref.id}
        resp.update(_serialize_doc(saved_data or {}))
        return resp

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("visited の upsert に失敗しました: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/read_visitor")
async def read_visitor(payload: VisitorByID):
    try:
        doc = firestore_client.collection(FIRESTORE_COLLECTION_NAME).document(
            payload.visitor_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="アイテムが見つかりません")
        return _serialize_doc(doc.to_dict() or {})
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("アイテム %s の読み取りに失敗しました: %s", payload.visitor_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
