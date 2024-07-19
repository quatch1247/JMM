from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import pandas as pd
from app.gpt.weather import get_weather_info
from app.gpt.kakao_location_search import get_location_data_json
from app.gpt.naver_location_search import search_restaurants, sort_restaurants_by_distance

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/get-my-weather", response_model=str)
async def get_weather():
    try:
        result = get_weather_info()
        if "오류 발생" in result:
            raise HTTPException(status_code=500, detail=result)
        if "위치 정보가 데이터베이스에 없습니다" in result:
            raise HTTPException(status_code=404, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-places-kakao", response_model=str)
async def get_places(query: str, latitude: float, longitude: float, radius: int = 10000, category_group_code: str = 'FD6'):
    try:
        json_result = get_location_data_json(query, longitude, latitude, radius, category_group_code)
        return json_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-places-naver", response_model=str)
async def get_places_naver(query: str, latitude: float, longitude: float):
    try:
        search_results = search_restaurants(query)
        sorted_data = sort_restaurants_by_distance(search_results, latitude, longitude)
        
        result_list = [{
            'address_name': restaurant['address'],
            'place_name': restaurant['title'],
            'place_url': restaurant['link'],
            'distance': round(restaurant['distance'], 2)
        } for restaurant in sorted_data]

        return pd.DataFrame(result_list).to_json(orient='records', force_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
