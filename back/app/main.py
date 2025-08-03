import asyncio
import aiohttp
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from app.llama_utils import analyze_receipt  # Import the async version

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

async def preload_model():
    try:
        print("모델 preload 중...")
        async with aiohttp.ClientSession() as session:
            for _ in range(10):  # 10번 시도 (총 30초)
                try:
                    async with session.post(
                        "http://ollama:11434/api/generate",
                        json={"model": "gemma3:4b", "prompt": "모델 로딩 테스트입니다.", "stream": False},
                    ) as response:
                        response.raise_for_status()
                        print("모델 preload 성공:", (await response.json()).get("response", ""))
                        break
                except Exception:
                    await asyncio.sleep(3)  # 3초 대기 후 재시도
            else:
                raise Exception("모델 preload 실패: 타임아웃")
    except Exception as e:
        print("모델 preload 실패:", e)

@app.on_event("startup")
async def startup_event():
    await preload_model()

@app.post("/analyze_receipt", response_model=ReceiptResponse)
async def analyze_receipt_endpoint(file: UploadFile = File(...)):
    upload_dir = "uploaded_images"
    os.makedirs(upload_dir, exist_ok=True)

    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    date, total = await analyze_receipt(file_location)  # Await the async function
    response = ReceiptResponse(date=date, total=total)
    print(response)
    return response

@app.get("/test")
async def test():
    return {"message": "Server is running"}