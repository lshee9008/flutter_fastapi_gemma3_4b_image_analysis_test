from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import shutil
import os
from app.llama_utils import analyze_receipt

app = FastAPI()

# CORS settings for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReceiptResponse(BaseModel):
    date: str
    total: str

def preload_model():
    try:
        print("모델 preload 중...")
        response = requests.post(
            "http://ollama:11434/api/generate",
            json={
                "model": "gemma3:4b",
                "prompt": "모델 로딩 테스트입니다.",
                "stream": False,
            }
        )
        print("모델 preload 성공:", response.json().get("response", ""))
    except Exception as e:
        print("모델 preload 실패:", e)

@app.on_event("startup")
async def startup_event():
    preload_model()

@app.post("/analyze_receipt", response_model=ReceiptResponse)
async def analyze_receipt(file: UploadFile = File(...)):
    upload_dir = "uploaded_images"
    os.makedirs(upload_dir, exist_ok=True)

    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    date, total = analyze_receipt(file_location)
    response = ReceiptResponse(date=date, total=total)
    print(response)
    return response

# Add a test endpoint for debugging
@app.get("/test")
async def test():
    return {"message": "Server is running"}