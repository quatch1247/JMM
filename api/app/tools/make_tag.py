from sqlalchemy.orm import Session
from database import SessionLocal
# from models import StoresWithinRange, Tag
from models import StoresWithinRange
from openai import OpenAI
import openai
import logging
import time
from config import get_settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("tag.log"),
    logging.StreamHandler()
])

settings = get_settings()
openai.api_key = settings.openai_api_key


def get_tags_from_description(description):
    from openai import OpenAI
    system_prompt = (
        "당신은 주어진 식당 정보를 바탕으로 태그를 생성하는 태그 생성 봇입니다.\n"
        "주어진 식당 정보에 나와 있는 음식 메뉴와 부가정보를 보고. 메뉴들에 대한 태그들을 생성해주세요.\n"
        "태그를 생성할 때 다음과 같은 항목을 고려해서 생성해주세요: "
        "1. 맛: 음식 메뉴의 주요 맛 (예: #매운맛, #달콤한맛 #상큼한맛 ...)"
        "2. 식감: 메뉴의 주요 식감 (예: #바삭한식감, #부드러운식감 ...)"
        "3. 분류: 메뉴의 음식 종류 (예: #샌드위치, #치킨, #국밥, #제육볶음 ...)"
        "4. 조리 방법: " 
        "4. 날씨: 어떤 날씨에 어울리는지 (예: #더운날, #비오는날, #눈오는날)"
    )
    
    user_prompt = (
        f"다음은 식당 정보입니다. 이 정보를 바탕으로 식당 정보를 요약해줘:\n"
        f"식당 정보: {description}\n"
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
            tags = response.choices[0].message.content
            return tags
        except Exception as e:
            logging.error(f"Summarization attempt {i+1} failed: {e}")
            if i < retries - 1:
                time.sleep(2 ** i)
                continue
            else:
                raise RuntimeError(f"Error in summarization: {e}")

def create_tags_for_single_store(store_id):
    db: Session = SessionLocal()
    
    try:
        store = db.query(StoresWithinRange).filter(StoresWithinRange.id == store_id).first()
        
        if store and store.raw_description:
            tags = get_tags_from_description(store.raw_description)
            print(tags)
            # for tag_name in tags:
            #     if tag_name:
            #         tag = Tag(store_id=store.id, name=tag_name)
            #         db.add(tag)
            # db.commit()
            print("Tags have been successfully added to the database.")
        else:
            print("Store not found or raw_description is empty.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    # 테스트를 위한 임의의 store_id
    test_store_id = 7  # 실제 store_id로 변경하여 테스

    create_tags_for_single_store(test_store_id)
