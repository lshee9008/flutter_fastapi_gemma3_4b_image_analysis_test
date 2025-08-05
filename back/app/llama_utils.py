import aiohttp
import base64

def encode_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

async def analyze_receipt(image_path: str) -> tuple[str, str]:
    base64_image = encode_image_base64(image_path)

    prompt = "이 이미지는 영수증입니다. 결제한 영수증 발급 날짜와 결제된 판매 결제 금액을 아래 형식으로 알려주세요:\n\n날짜: YYYY-MM-DD\n합계: 숫자, 포인트는 절대 읽지 마십시오. 무조건 결제되는 사업자가 받을 금액을 분석하십시오."

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "gemma3:4b",  # 또는 gemma3:4b 기반의 이미지 처리 가능한 버전
                    "prompt": prompt,
                    "images": [base64_image],
                    "stream": False
                },
                timeout=aiohttp.ClientTimeout(total=180)
            ) as response:
                response.raise_for_status()
                output = (await response.json()).get("response", "").strip()
                print("----- LLM OUTPUT -----")
                print(output)
                print("----------------------")

                # 정규표현식 추출
                import re
                date_match = re.search(r"날짜\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})", output)
                total_match = re.search(r"합계\s*[:\-]?\s*(\d+)", output)

                date = date_match.group(1).strip() if date_match else "날짜 추출 실패"
                total = total_match.group(1).strip() if total_match else "합계 추출 실패"

                return date, total

    except aiohttp.ClientError as e:
        print(f"오류 발생: {e}")
        return "날짜 추출 실패", "합계 추출 실패"
