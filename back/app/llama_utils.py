import aiohttp
import re

async def analyze_receipt(image_path: str) -> tuple[str, str]:
    prompt = f"""
이 이미지는 영수증 사진입니다. 이 영수증 사진을 분석해주고 날짜와 결제된 금액을 한국어로 분석하여 다음 형식으로 알려주세요:

날짜: (YYYY-MM-DD 형식, 예: 2025-08-03)
합계: (숫자만, 예: 15000, 결제된 금액)

형식을 반드시 지켜주세요. 예:
날짜: 2025-08-03
합계: 15000

(이미지를 직접 분석했다고 가정하고 텍스트로 설명하세요.)
"""

    try:
        print("Sending image analysis request to Gemma3:4b")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "gemma3:4b",
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=aiohttp.ClientTimeout(total=180)
            ) as response:
                response.raise_for_status()
                output = (await response.json()).get("response", "").strip()
                print("----- RAW LLaMA OUTPUT -----")
                print(repr(output))
                print("----------------------------")

                date_match = re.search(r"날짜\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})", output)
                total_match = re.search(r"합계\s*[:\-]?\s*(\d+)", output)

                date = date_match.group(1).strip() if date_match else "날짜 추출 실패"
                total = total_match.group(1).strip() if total_match else "합계 추출 실패"

                print(f"Parsed date: {date}, total: {total}")
                return date, total

    except aiohttp.ClientError as e:
        print(f"Error while calling Ollama: {e}")
        return "날짜 추출 실패", "합계 추출 실패"
