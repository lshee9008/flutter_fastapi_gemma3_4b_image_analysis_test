FROM python:3.11-slim

# Tesseract와 한국어 언어 데이터 설치
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-kor

COPY requirements.txt .
RUN pip install -r requirements.txt

# Tesseract와 한국어 언어 데이터 설치
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-kor

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]