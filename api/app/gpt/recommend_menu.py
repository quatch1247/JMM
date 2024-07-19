import openai
from config import get_settings
import random

def get_openai_response(weather_info: str) -> str:
    settings = get_settings()
    openai.api_key = settings.openai_api_key

    system_prompt = (
        "당신은 지역을 기반으로 음식 메뉴를 추천하는 추천 봇입니다.\n"
        "회사에서 일하다가 점심 식사로 먹기로 적절한 음식 메뉴를 중복되지 않게 랜덤으로 추천해줘.\n"
        "패스트푸드, 한식, 일식, 중식, 양식, 분식 등 최대한 많은 다양한 음식 후보군에서 적절한 메뉴를 추천해줘.\n"
        "날씨를 신경 쓰지말고 지역을 우선으로 고려해줘"
        "이런 식으로 메뉴를 하나만 구체적으로 도출해줘.\n"
        "그리고 응답을 줄 때, 메뉴와 함께 선택한 이유를 날씨와 연관지어서 다음 형식으로 알려줘. (음식 메뉴)-_-(음식 메뉴를 선택한 이유)\n"
        "ex) KFC-_-날씨도 더운데, 간편하게 먹을 수 있고, 치킨을 먹으면 기분이 좋아져요!\n"
        "ex) 냉면-_-더운 여름에 먹기 좋은 시원한 면 요리로, 갈증 해소에 좋아요."
    )
    user_prompt = "위치 및 날씨정보 : " + weather_info
    print(user_prompt)
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=1.0,
            frequency_penalty=2,
            presence_penalty=2,
            n=10
        )
        random_choice = random.choice(response.choices)
        return random_choice.message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    weather_info = "2024년 07월 11일 14시 24분에 서울특별시 종로구 사직동 지역(60, 127)의 날씨는 구름많음이며, 강수 없음 (시간당 강수없음mm), 기온은 27.0℃, 습도는 65.0%, 풍속은 WSW 방향으로 3m/s입니다."
    response_text = get_openai_response(weather_info)
    print(response_text)
