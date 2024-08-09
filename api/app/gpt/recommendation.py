from app.gpt.weather import get_weather_info
import random
import base64
import json
import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Menu, StoresWithinRange, Image
from app.gpt.weather import get_weather_info, md_get_weather_info
import openai
from app.config import get_settings
import re
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

settings = get_settings()
openai.api_key = settings.openai_api_key

class RecommendationTracker:
    def __init__(self):
        self.recent_recommendations = []

    def update_recommendations(self, new_id):
        if len(self.recent_recommendations) >= 3:
            self.recent_recommendations.pop(0)
        self.recent_recommendations.append(new_id)

    def is_recently_recommended(self, store_id):
        return store_id in self.recent_recommendations

recommendation_tracker = RecommendationTracker()

def fetch_all_menus():
    db = SessionLocal()
    try:
        menus = db.query(Menu).all()
        store_menus = {}
        for menu in menus:
            if menu.store_id not in store_menus:
                store_menus[menu.store_id] = []
            store_menus[menu.store_id].append(menu.menu)
        
        for store_id in store_menus:
            random.shuffle(store_menus[store_id])
            
        return store_menus
    finally:
        db.close()

def recommend_menu_based_on_weather():
    weather_info = get_weather_info()
    md_weather_info = md_get_weather_info()
    store_menus = fetch_all_menus()
    
    system_prompt = (
        "당신은 날씨에 따라 다양한 메뉴를 추천하는 메뉴 추천 전문가입니다.\n"
        "다음 로직에 따라 step-by-step으로 해당 메뉴를 가진 식당의 ID를 선택해주세요\n"
        "1. 주어진 메뉴를 보고 온도와 습도를 고려해서 음식을 랜덤으로 선택해주세요.\n"
        "2. 그 메뉴를 보유하고 있는 식당 ID와 선택한 이유를 현재 날씨와 연관지어서 논리적으로 설명해주세요.\n"
        "3. 응답 형식은 반드시 다음과 같습니다.\n"
        "주어지는 메뉴 형식 : 식당 ID : ['메뉴1', '메뉴2', '메뉴3', '메뉴4', '메뉴5', '메뉴6', '메뉴7'], \n"
        "응답형식 : (식당 ID)-_-(선택한 이유)입니다.\n"
        "다음 예시들은 참고만 하되 메뉴를 따라하지 마세요.\n"
        "101-_-뜨끈한 국물 요리는 몸을 따뜻하게 해주고, 편안한 느낌을 줍니다. 이런 날씨에는 국물이 있는 음식이 제격이죠\n"
        "102-_-전골은 다양한 재료가 어우러져 깊은 맛을 내고, 따뜻하게 데워줘서 비 오는 날씨와 잘 어울립니다\n"
        "103-_-매콤한 찌개는 비 오는 날의 우울함을 날려줄 수 있어요. 매운 음식은 기분 전환에 좋습니다\n"
        "104-_-한국식 라면은 언제나 인기 있는 선택입니다. 특히 비 오는 날엔 더 맛있게 느껴지죠\n"
        "105-_-따뜻한 비빔밥은 여러 가지 재료가 어우러져 건강에도 좋고, 기분 전환에도 도움을 줍니다\n"
        "106-_-전골은 가족이나 친구와 나누기에도 좋은 음식입니다. 따뜻한 음식을 나누며 정을 나누세요\n"
        "107-_-매운 해물탕은 비 오는 날의 쌀쌀함을 날려주고, 몸을 따뜻하게 해줍니다\n"
        "108-_-국밥은 언제나 옳습니다. 특히 비 오는 날엔 더욱 맛있고 든든하게 느껴지죠\n"
        "109-_-따뜻한 국물이 있는 음식을 추천합니다. 날씨와 잘 어울리고 몸을 데워주니까요\n"
        "다시 한번 강조하자면, 반복되는 답변이 생성되면 안되니 최대한 메뉴 선택을 신박하게 해주세요."
    )

    weather_prompt = f"현재 날씨 정보: {weather_info}\n"
    menu_prompt = f"메뉴 목록: {json.dumps(store_menus, ensure_ascii=False)}\n"

    user_prompt = weather_prompt + menu_prompt + "날씨에 적절한 한가지 메뉴를 랜덤하게 고르고, 해당 메뉴를 보유한 식당 ID와 고른 이유를 부연설명 없이 (식당ID)-_-(선택한 이유)이 형태로 알려줘."
    
    client = OpenAI()

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            frequency_penalty=2.0,
            presence_penalty=2.0,
            max_tokens=4096
        )

        result = response.choices[0].message.content
        store_id, reason = result.split('-_-')

        store_id = re.sub(r'[()]', '', store_id.strip())

        db = SessionLocal()
        try:
            store_info = db.query(StoresWithinRange).filter(StoresWithinRange.id == store_id).first()
            image_record = db.query(Image).filter(Image.store_id == store_id).first()
            image_data = base64.b64encode(image_record.image).decode('utf-8') if image_record else None

            if store_info:
                business_name = store_info.business_name
                if len(recommendation_tracker.recent_recommendations) < 3:
                    if recommendation_tracker.is_recently_recommended(business_name):
                        continue
                recommendation_tracker.update_recommendations(business_name)
                return {
                    "business_name": business_name,
                    "business_type": store_info.business_type,
                    "weather_info": md_weather_info,
                    "store_id": store_id,
                    "reason": reason.strip(),
                    "url": store_info.url,
                    "image_data": f"![image](data:image/png;base64,{image_data})" if image_data else None,
                }
        except Exception as e:
            print(f"Database query error: {e}")
        finally:
            db.close()

def fetch_random_ai_summarize_with_image():
    db = SessionLocal()
    try:
        store_ids = db.query(StoresWithinRange.id).all()
        random_id = random.choice(store_ids)[0]

        store_info = db.query(StoresWithinRange).filter(StoresWithinRange.id == random_id).first()

        image_record = db.query(Image).filter(Image.store_id == random_id).first()
        image_data = base64.b64encode(image_record.image).decode('utf-8') if image_record else None

        ai_summarize = store_info.ai_summarize
        ai_summarize = re.sub(r'\n\n', ' ', ai_summarize)
        ai_summarize = re.sub(r'\n', ' ', ai_summarize)    
        print(ai_summarize)
        return {
            "business_name": store_info.business_name,
            "business_type": store_info.business_type,
            "ai_summarize": ai_summarize,
            "image_data": f"![image](data:image/png;base64,{image_data})" if image_data else None,
        }
    finally:
        db.close()

def fetch_random_ai_summarize_with_image_is_in_building():
    db = SessionLocal()
    try:
        store_ids = db.query(StoresWithinRange.id).filter(StoresWithinRange.is_in_company_building == True).all()
        if not store_ids:
            return None
        
        valid_store_ids = [store_id[0] for store_id in store_ids if not recommendation_tracker.is_recently_recommended(store_id[0])]
        if not valid_store_ids:
            return None

        random_id = random.choice(valid_store_ids)

        recommendation_tracker.update_recommendations(random_id)

        store_info = db.query(StoresWithinRange).filter(StoresWithinRange.id == random_id).first()

        image_record = db.query(Image).filter(Image.store_id == random_id).first()
        image_data = base64.b64encode(image_record.image).decode('utf-8') if image_record else None

        ai_summarize = store_info.ai_summarize
        ai_summarize = re.sub(r'\n\n', ' ', ai_summarize)
        ai_summarize = re.sub(r'\n', ' ', ai_summarize)
        print(ai_summarize)
        return {
            "business_name": store_info.business_name,
            "business_type": store_info.business_type,
            "ai_summarize": ai_summarize,
            "image_data": f"![image](data:image/png;base64,{image_data})" if image_data else None,
        }
    finally:
        db.close()


if __name__ == "__main__":
    result1 = recommend_menu_based_on_weather()
    print(result1)
    # result2 = fetch_random_ai_summarize_with_image()
    # print(result2)
    # result3 = fetch_random_ai_summarize_with_image_is_in_building()
    # print(result3)
