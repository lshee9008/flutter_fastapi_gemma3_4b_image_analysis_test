import requests
import re
from PIL import Image
import pytesseract

def extract_text_from_image(image_path: str) -> str:
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='kor+eng')
        return text
    except Exception as e:
        print(f"Error in OCR: {e}")
        return ""

def analyze_receipt(image_path: str) -> tuple[str, str]:
    receipt_text = extract_text_from_image(image_path)
    if not receipt_text:
        return "OCR 실패", "분석 실패"

    prompt = f"""
다음은 영수증에서 추출한 텍스트입니다. (꼭! 한국어로 작성해주세요.)
무조건 한국어로 작성해주세요!

\"\"\"{receipt_text}\"\"\"

이 영수증을 분석한 후 아래 형식으로 날짜와 합계 가격을 추출해 주세요:

날짜: (YYYY-MM-DD 형식, 예: 2025-08-03)
합계: (숫자만, 예: 15000)

형식을 반드시 지켜주세요. 예:
날짜: 2025-08-03
합계: 15000
"""

    try:
        print(f"Sending request to Ollama for receipt text: {receipt_text}")
        response = requests.post(
            "http://ollama:11434/api/generate",
            json={
                "model": "gemma3:4b",
                "prompt": prompt,
                "stream": False,
            },
            timeout=180
        )
        response.raise_for_status()

        output = response.json().get("response", "").strip()
        print("----- RAW LLaMA OUTPUT -----")
        print(repr(output))
        print("----------------------------")

        date_match = re.search(
            r"날짜\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})",
            output,
            re.DOTALL
        )

        total_match = re.search(
            r"합계\s*[:\-]?\s*(\d+)",
            output,
            re.DOTALL
        )

        date = date_match.group(1).strip() if date_match else "날짜 추출 실패"
        total = total_match.group(1).strip() if total_match else "합계 추출 실패"

        print(f"Parsed date: {date}, total: {total}")
        return date, total

    except requests.exceptions.RequestException as e:
        print(f"Error while calling Ollama: {e}")
        return "날짜 추출 실패", "합계 추출 실패"