import requests
import math
from app.config import get_settings

settings = get_settings()


client_id = settings.naver_open_api_client_id
client_secret = settings.naver_open_api_client_secret

def search_restaurants(query, display=5, start=3, sort='random'):
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"API 호출 중 오류 발생: {e}")
        return None
    
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def sort_restaurants_by_distance(data, target_lat, target_lon):
    if not data or 'items' not in data:
        return []

    restaurants = data['items']
    for restaurant in restaurants:
        restaurant_lat = int(restaurant['mapy']) / 10000000
        restaurant_lon = int(restaurant['mapx']) / 10000000
        restaurant['distance'] = haversine(target_lat, target_lon, restaurant_lat, restaurant_lon)

    sorted_restaurants = sorted(restaurants, key=lambda x: x['distance'])
    return sorted_restaurants

if __name__ == "__main__":

    target_lat = 37.57384225497904
    target_lon = 126.97507309813098
    
    query = "서울특별시 종로구 필운동 146-1 아이에스빌딩 1층"
    search_results = search_restaurants(query)
    # print(search_results)
    
    sorted_data = sort_restaurants_by_distance(search_results, target_lat, target_lon)
    
    # 결과 출력
    for restaurant in sorted_data:
        print(f"{restaurant['title']}: {restaurant['distance']} km")
    
    
    

    

    
    