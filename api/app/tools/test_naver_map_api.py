import requests
import logging
import math

# 로깅 설정
logging.basicConfig(filename='geocode.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Naver API 설정
client_id = 'ocxgqkoxcu'  # 여기에 Naver API Client ID를 입력하세요
client_secret = '33PZUVSK9BnevfsY0XVddDlhXwxqfH57AmUCoytr'  # 여기에 Naver API Client Secret을 입력하세요

def get_coordinates(address):
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    params = {
        "query": address,
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("Response JSON:", data)  # 응답을 출력하여 확인
        if data['status'] == 'OK' and data['meta']['totalCount'] > 0:
            address_info = data['addresses'][0]
            x = address_info['x']
            y = address_info['y']
            return float(y), float(x)  # 위도(y), 경도(x)의 순서로 반환
        else:
            logging.error(f"No results found for address: {address}")
            return None, None
    else:
        logging.error(f"Error {response.status_code}: {response.text}")
        return None, None

if __name__ == "__main__":
    # 테스트할 주소 입력
    address = "서울특별시 종로구 종로1가 24 르메이에르종로타운1"
    latitude, longitude = get_coordinates(address)
    
    # 비교할 좌표 (위도, 경도)
    Latitudexx = 37.5736565
    Longitudexx = 126.9742286
    
    if longitude and latitude:
        print(f"Address: {address}")
        print(f"Longitude: {longitude}, Latitude: {latitude}")
        
    else:
        print(f"Failed to get coordinates for address: {address}")
