import requests
import pandas as pd
import math
from app.config import get_settings

settings = get_settings()

api_key = settings.kakao_api_key

def haversine(lon1, lat1, lon2, lat2):
    R = 6371
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def elec_location(region, page_num, entries_limit):
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    params = {'query': region, 'page': page_num, 'size': entries_limit}
    headers = {"Authorization": f"KakaoAK {api_key}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"API 호출 실패: {response.status_code}")
        return [], 0
    
    data = response.json()
    places = data.get('documents', [])
    total = data.get('meta', {}).get('total_count', 0)
    
    if total > 45:
        print(f"{total}개 중 최대 45개의 데이터만 가져옵니다.")
    
    return places, total

def elec_info(places):
    data = [{
        'ID': place['id'],
        'stores': place['place_name'],
        'X': float(place['x']),
        'Y': float(place['y']),
        'road_address': place['road_address_name'],
        'place_url': place['place_url']
    } for place in places]
    
    return pd.DataFrame(data)

def keywords(location_names, max_entries=None):
    all_data_frames = []
    total_entries = 0
    for location in location_names:
        page_num = 1
        while True:
            entries_left = None if max_entries is None else max_entries - total_entries
            if entries_left is not None and entries_left <= 0:
                break
            entries_to_fetch = 15 if entries_left is None or entries_left > 15 else entries_left
            places, count = elec_location(location, page_num, entries_to_fetch)
            if not places:
                break
            df_temp = elec_info(places)
            all_data_frames.append(df_temp)
            total_entries += len(df_temp)
            if max_entries is not None and total_entries >= max_entries:
                break
            page_num += 1
            
    if all_data_frames:
        df = pd.concat(all_data_frames, ignore_index=True)
        df = df.drop_duplicates(subset=['ID'])
        return df
    else:
        return pd.DataFrame()

def get_location_data_json(location_keywords, target_lat, target_lon, max_entries=None):
    print(location_keywords)
    df = keywords(location_keywords, max_entries)
    
    if df.empty:
        return "검색된 결과가 없습니다."

    df['distance'] = df.apply(lambda row: haversine(target_lon, target_lat, row['X'], row['Y']), axis=1)
    df = df.sort_values(by='distance')
    
    for idx, row in df.iterrows():
        print(f"{row['stores']} - 거리: {row['distance']:.2f} km")
    
    df.reset_index(drop=True, inplace=True)
    json_result = df.to_json(orient='records', force_ascii=False)
    return json_result

def get_place_count(query, longitude, latitude, radius, category_group_code):
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    params = {
        'query': query,
        'x': longitude,
        'y': latitude,
        'radius': radius,
        'category_group_code': category_group_code,
        'size': 15 
    }
    headers = {"Authorization": f"KakaoAK {api_key}"}

    total_count = 0
    places = []
    page_num = 1
    
    while True:
        params['page'] = page_num
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"API 호출 실패: {response.status_code}")
            break
        
        data = response.json()
        total_count = data['meta']['total_count']
        places.extend(data['documents'])
        
        if len(data['documents']) < 15 or len(places) >= 45:
            break
        
        page_num += 1
    
    return total_count, places[:45]

def get_location_data_json(query, longitude, latitude, radius, category_group_code='FD6'):
    total_count, places = get_place_count(query, longitude, latitude, radius, category_group_code)
    result_list = []

    for place in places:
        distance = haversine(longitude, latitude, float(place['x']), float(place['y']))
        result = {
            'address_name': place['address_name'],
            'place_name': place['place_name'],
            'place_url': place['place_url'],
            'distance': round(distance, 2)
        }
        result_list.append(result)

    result_list = sorted(result_list, key=lambda x: x['distance'])
    
    return pd.DataFrame(result_list).to_json(orient='records', force_ascii=False)

if __name__ == "__main__":
    query = '너와나실내마차'
    longitude = 126.97419295352408
    latitude = 37.573857833264
    radius = 10000
    category_group_code = 'FD6'
    
    json_result = get_location_data_json(query, longitude, latitude, radius, category_group_code)
    print(json_result)
    
