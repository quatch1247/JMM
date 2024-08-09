from fastapi import APIRouter, HTTPException
from app.gpt.recommendation import fetch_random_ai_summarize_with_image, fetch_random_ai_summarize_with_image_is_in_building, recommend_menu_based_on_weather
from app.gpt.search_with_ai import execute_sql_agent
import time

router = APIRouter(prefix="/recommendation", tags=["recommendation"])

@router.get("/random-recommendation")
def get_random_ai_summarize():
    try:
        time.sleep(1.5)
        markdown_response = fetch_random_ai_summarize_with_image()
        return markdown_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/random-recommendation-is-in-building")
def get_random_ai_summarize_is_in_building():
    try:
        time.sleep(1.5)
        markdown_response = fetch_random_ai_summarize_with_image_is_in_building()
        return markdown_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/recommendation_based_on_weather")
def get_response_based_on_weather():
    try:
        markdown_response = recommend_menu_based_on_weather()
        return markdown_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sql-agent")
def get_sql_agent_response(user_input: str):
    try:
        response = execute_sql_agent(user_input)
        return {"result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
    
    