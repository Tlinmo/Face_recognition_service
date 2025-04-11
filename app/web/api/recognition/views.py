import imghdr
from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException
from loguru import logger
import numpy as np
import cv2

from app.log import configure_logging
from app.services.recognition.recognition import RecognitionService
from app.services.models.face import Face
from app.web.api.recognition import schema

configure_logging()

router = APIRouter()
reco = RecognitionService(name="buffalo_l", providers=["CPUExecutionProvider"])
reco.prepare(ctx_id=0, det_size=(640, 640))


@router.post("/", response_model=List[schema.FaceEmbedding])
async def image_to_embedding(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="Загруженный файл не является изображением."
        )

    contents = await file.read()

    if imghdr.what(None, contents) is None:
        raise HTTPException(
            status_code=400, detail="Загруженный файл не является изображением."
        )

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=400, detail="Не удалось декодировать изображение."
        )

    faces = reco.detect(image)
    if not faces:
        raise HTTPException(status_code=404, detail="Лица не обнаружены.")

    reco.recognize(image, faces)
    embeddings = [face.embedding for face in faces if hasattr(face, "embedding")]

    return [Face(embedding=embedding.tolist()) for embedding in embeddings]
