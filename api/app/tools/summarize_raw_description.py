import os
import time
import logging
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from config import get_settings
from openai import OpenAI

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("app.log"),
    logging.StreamHandler()
])

settings = get_settings()
OpenAI.api_key = settings.openai_api_key

def get_summary(store):
    from openai import OpenAI
    system_prompt = (
        "당신은 도렴빌딩에서 일하는 직원들에게 건물 주변 지역의 해당 식당 정보를 깔끔하게 요약해주는 요약 AI 봇입니다.\n"
        "주어진 정보를 바탕으로 다음 형식에 따라 정보들을 정리해서 mark-down 형식으로 보여주세요.\n"
        "다음 정보들을 개행할 때마다 DB에 개행 문자가 포함되어 저장되도록 주어진 형식을 참고하여 반드시 각 항목 뒤에(<br>)를 표시해서 요약해서 알려주세요.\n"
        "각 항목에서 '주요 메뉴 및 가격'항목전에 <br>이 두번, 'AI 요약'항목 전에 <br>이 두번 들어가야합니다.\n"
        "주어진 메뉴명 및 가격은 주어진 정보에 따라 유동적으로 대표적인 메뉴 5개만 보여주세요.\n"
        "AI 요약은 가격, 메뉴 등 주어진 정보들을 최대한 활용하여 최대한 사람이 사람에게 설명하듯이 존댓말로 요약해주세요."
        "형식 :\n\n"
        "#기본 정보\\<br>"
        "- **주소:** (주어진 식당 주소)\\<br>"
        "- **지도:** (주어진 지도 링크)\\<br>\\<br>"
        "주요 메뉴 및 가격\\<br>"
        "1. **(주어진 메뉴명 1)** - (주어진 가격 1)\\<br>"
        "2. **(주어진 메뉴명 2)** - (주어진 가격 2)\\<br>"
        "3. **(주어진 메뉴명 3)** - (주어진 가격 3)\\<br>"
        "4. **(주어진 메뉴명 4)** - (주어진 가격 4)\\<br>\\<br>"
        "AI 요약\\<br>"
        "- (AI의 객관적인 의견)\\<br>"
        "- (AI의 주관적인 의견)\\<br>"
        "- (AI가 추천하는 이유1)\\<br>"
        "- (AI가 추천하는 이유2)\\<br>"
        "- (AI가 추천하는 이유3)\\<br>\\<br>"
    )

    user_prompt = (
        f"다음은 식당 정보입니다. 이 정보를 바탕으로 식당 정보를 요약해줘:\n"
        f"식당 주소: {store.address}\n"
        f"지도 링크: {store.url}\n"
        f"도렴빌딩 건물 내 여부: {'네' if store.is_in_company_building else '아니요'}\n"
        f"메뉴 및 가격 설명: {store.raw_description}\n"
        f"이 정보를 바탕으로 요약해 주세요."
    )

    retries = 3
    for i in range(retries):
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2048
            )
            summary = response.choices[0].message.content
            return summary
        except Exception as e:
            logging.error(f"Summarization attempt {i+1} failed: {e}")
            if i < retries - 1:
                time.sleep(2 ** i)
                continue
            else:
                raise RuntimeError(f"Error in summarization: {e}")

def summarize_all_descriptions():
    from models import StoresWithinRange 
    db = SessionLocal()

    try:
        stores = db.query(StoresWithinRange).all()

        for store in stores:
            if store.raw_description:
                summarized = get_summary(store)
                store.ai_summarize = summarized
                db.add(store)
                db.commit()
                logging.info(f"Store ID: {store.id}, Summarized: {summarized}\n")

    finally:
        db.close()
        
def summarize_selected_descriptions(store_ids):
    from models import StoresWithinRange 
    db = SessionLocal()

    try:
        stores = db.query(StoresWithinRange).filter(StoresWithinRange.id.in_(store_ids)).all()

        for store in stores:
            if store.raw_description:
                summarized = get_summary(store)
                store.ai_summarize = summarized
                db.merge(store)
                db.commit()
                logging.info(f"Store ID: {store.id}, Summarized: {summarized}\n")

    finally:
        db.close()

if __name__ == "__main__":
    # summarize_all_descriptions()
    # 특정 ID를 가진 데이터만 다시 요약하려면 다음 함수를 사용하세요
    # 예: summarize_selected_descriptions([1, 2, 3])
    summarize_selected_descriptions([73])