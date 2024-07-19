# from kakao_location_search import get_location_data_json
# from weather import get_weather_info
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from config import get_settings
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

settings = get_settings()

# 도구 정의
@tool
def fetch_weather_info(lat: float, lon: float) -> str:
    """
    Fetches weather information for the given latitude and longitude.

    Args:
    lat (float): Latitude of the location.
    lon (float): Longitude of the location.

    Returns:
    str: Weather information.
    """
    return get_weather_info(lat, lon)

@tool
def get_restaurants_info(query: str, longitude: float, latitude: float, radius: int, category_group_code: str) -> dict:
    """
    Fetches location data based on given parameters.

    Args:
    query (str): Search query.
    longitude (float): Longitude of the location.
    latitude (float): Latitude of the location.
    radius (int): Search radius in meters.
    category_group_code (str): Category group code for the search.

    Returns:
    dict: JSON response containing location data.
    """
    return get_location_data_json(query, longitude, latitude, radius, category_group_code)

# 에이전트 설정
llm = ChatOpenAI(model="gpt-4", api_key=settings.openai_api_key)

@tool
def suggest_lunch_menu_based_on_weather(weather_info: str) -> str:
    """
    Suggests a lunch menu based on the given weather information.

    Args:
    weather_info (str): Weather information.

    Returns:
    str: Suggested lunch menu.
    """
    prompt = f"현재 날씨 정보는 다음과 같습니다: {weather_info}. 이 날씨에 적합한 점심 메뉴를 추천해주세요."
    print(f"Prompt for LLM: {prompt}")
    response = llm.invoke({"prompt": prompt})
    print(f"LLM Response: {response}")
    return response["choices"][0]["text"]

tools = [
    get_restaurants_info,
    fetch_weather_info,
    suggest_lunch_menu_based_on_weather
]

prompt_template = PromptTemplate(
    input_variables=["query", "longitude", "latitude", "radius", "category_group_code", "agent_scratchpad"],
    template="""
    You are an assistant that helps plan and execute tasks.

    1. Use the 'fetch_weather_info' tool to get the current weather for the provided location.
    2. Based on the weather, use the 'suggest_lunch_menu_based_on_weather' tool to suggest a specific type of lunch menu (e.g., 메밀국수, 수육국밥).
    3. Use the 'get_restaurants_info' tool to find restaurants serving that menu within the specified radius.

    Query: {query}
    Longitude: {longitude}
    Latitude: {latitude}
    Radius: {radius}
    Category Group Code: {category_group_code}

    Plan:
    {agent_scratchpad}
    """
)

agent = create_tool_calling_agent(llm, tools, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def plan_and_execute_agent(query: str, longitude: float, latitude: float, radius: int, category_group_code: str) -> str:
    plan_result = agent_executor.invoke({
        "query": query,
        "longitude": longitude,
        "latitude": latitude,
        "radius": radius,
        "category_group_code": category_group_code
    })
    
    # 실행 계획 분석 및 도구 호출
    output_plan = plan_result.get('output', '')
    print("Execution Plan:", output_plan)
    
    weather_info = None
    menu = None

    # 도구 호출
    for step in output_plan.split('\n'):
        if "fetch_weather_info" in step:
            weather_info = fetch_weather_info.invoke({"lat": latitude, "lon": longitude})
            print(f"Weather Info: {weather_info}")
        elif "suggest a specific type of lunch menu" in step and weather_info:
            menu = suggest_lunch_menu_based_on_weather(weather_info)
            print(f"Suggested Menu: {menu}")
        elif "get_restaurants_info" in step and menu:
            execution_result = get_restaurants_info.invoke({"query": menu, "longitude": longitude, "latitude": latitude, "radius": radius, "category_group_code": category_group_code})
            return execution_result

    return plan_result

# 에이전트를 사용하여 응답 받기
if __name__ == "__main__":
    query = "점심 메뉴를 추천해줘"
    longitude = 126.97419295352408
    latitude = 37.573857833264
    radius = 10000
    category_group_code = "FD6"
    response = plan_and_execute_agent(query, longitude, latitude, radius, category_group_code)
    print(response)
