from fastapi import APIRouter, HTTPException
from app.gpt.recommendation import fetch_random_ai_summarize_with_image, fetch_random_ai_summarize_with_image_is_in_building, recommend_menu_based_on_weather
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
    
    
    
    
    