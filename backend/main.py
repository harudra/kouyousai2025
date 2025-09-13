from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import firestore
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Firestore client will read emulator host from environment when using the emulator
def get_firestore_client():
    # If FIRESTORE_EMULATOR_HOST is set, the google-cloud-firestore client
    # will connect to the emulator automatically.
    # Project ID can be provided via FIRESTORE_PROJECT_ID env var or default.
    project = os.environ.get("FIRESTORE_PROJECT_ID", "demo-project")
    logger.debug("Creating Firestore client for project=%s", project)
    return firestore.Client(project=project)


class Item(BaseModel):
    name: str
    value: int


@app.post("/items")
async def create_item(item: Item):
    try:
        db = get_firestore_client()
        doc_ref = db.collection("items").document()
        item_data = item.model_dump()
        doc_ref.set(item_data)
        logger.info("Created item %s with id=%s", item_data, doc_ref.id)
        return {"id": doc_ref.id, **item_data}
    except Exception as e:
        logger.exception("Failed to create item: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    try:
        db = get_firestore_client()
        doc = db.collection("items").document(item_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="not found")
        return doc.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to read item %s: %s", item_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
