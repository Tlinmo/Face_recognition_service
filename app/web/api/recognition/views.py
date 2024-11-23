import imghdr

from fastapi import APIRouter, File, UploadFile, HTTPException
from loguru import logger
import numpy as np
import cv2

from app.log import configure_logging
from app.services.recognition.recognition import RecognitionService
from app.services.auth.embedding import Embedding
from app.web.api.recognition import schema

configure_logging()

router = APIRouter()
reco = RecognitionService()


@router.post("/", response_model=schema.VectorEmbedding)
async def image_to_embedding(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Загруженный файл не является изображением.")

    contents = await file.read()
    
    if imghdr.what(None, contents) is None:
        raise HTTPException(status_code=400, detail="Загруженный файл не является изображением.")

    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Не удалось декодировать изображение.")

    embedding = reco.get_embedding(img=image)
    
    
    return Embedding(vector=embedding.tolist())