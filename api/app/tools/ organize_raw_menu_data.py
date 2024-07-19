import os
import time
import logging
import json
import re
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from config import get_settings
from openai import OpenAI

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("menu.log"),
    logging.StreamHandler()
])

settings = get_settings()
OpenAI.api_key = settings.openai_api_key

def parse_raw_data(raw_description):
    from openai import OpenAI
    system_prompt = (
        "당신은 크롤링한 데이터를 활용이 용이하도록 정리해주는 데이터 분석 전문가 입니다.\n"
        "다음 raw_data를 부연설명 없이, 다음과 같은 형식으로 모든 메뉴를 형식화해서 반환하는 것이 목표입니다.\n"
        "반드시 -_- 와 ///을 사용해서 형식화시켜주세요."
        "(메뉴1)-_-(가격1)///(메뉴2)-_-(가격2)///(메뉴3)-_-(가격3)///(메뉴4)-_-(가격4)..."
        "메뉴는 단일 메뉴일수도, 복수의 메뉴일 수도 있습니다."
        "참고로 현재 크롤링한 raw_data에서 메뉴가 중복으로 적혀있는 경우가 있는데, 참고해서 적절하게 추출해주세요."
        "데이터에서 최대한 메뉴명과 그에 해당하는 가격만 추출할 수 있도록 노력해주세요."
    )

    user_prompt = (
        f"다음은 식당의 메뉴와 가격 정보가 있는 raw_data 입니다.\n"
        f"raw_data: {raw_description}\n"
        f"이 정보를 부연설명 없이, 다음과 같은 형식으로 모든 메뉴를 형식화해서 반환해줘.\n"
        f"반드시 -_- 와 ///을 사용해서 형식화시켜줘"
        f"(메뉴1)-_-(가격1)///(메뉴2)-_-(가격2)///(메뉴3)-_-(가격3)///(메뉴4)-_-(가격4)///..."
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

def parse_all_raw_description():
    from models import StoresWithinRange 
    db = SessionLocal()
    all_data = []

    try:
        stores = db.query(StoresWithinRange).all()

        for store in stores:
            if store.raw_description:
                parsed_data = parse_raw_data(store.raw_description)
                menu_items = parsed_data.split('///')
                menu_dict = {}
                for item in menu_items:
                    if '-_-' in item:
                        menu, price = item.split('-_-')
                        menu = re.sub(r'[\(\)]', '', menu).strip()  # 괄호만 제거
                        price = re.sub(r'[\(\)]', '', price).strip()  # 괄호만 제거
                        menu_dict[menu] = price
                    else:
                        logging.warning(f"Invalid format for item: {item}")
                store_data = {
                    "store_id": store.id,
                    "menu": menu_dict
                }
                all_data.append(store_data)
                logging.info(f"Store ID: {store.id}, parsed_data: {parsed_data}\n")
    finally:
        db.close()
    
    with open('parsed_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parse_all_raw_description()
