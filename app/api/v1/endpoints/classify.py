from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import joblib
import os

router = APIRouter()

# 모델 로드
# model_path = os.path.join(os.path.dirname(__file__), 'text_classification_model.pkl')
model_path = os.path.join('app', 'text_classification_model.pkl')
model = joblib.load(model_path)

class Texts(BaseModel):
    texts: List[str]

@router.post("/classify")
async def classify_texts(texts: Texts):
    predictions = model.predict(texts.texts)
    return {"predictions": predictions.tolist()}

