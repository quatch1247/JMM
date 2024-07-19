import requests
import logging

# 로깅 설정
logging.basicConfig(filename='directions.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Naver Directions 15 API 설정
client_id = 'ocxgqkoxcu'  # 여기에 Naver API Client ID를 입력하세요
client_secret = '33PZUVSK9BnevfsY0XVddDlhXwxqfH57AmUCoytr'  # 여기에 Naver API Client Secret을 입력하세요

def get_distance(start, goal):
    url = f"https://naveropenapi.apigw.ntruss.com/map-direction-15/v1/driving?start={start}&goal={goal}&option=trafast"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['code'] == 0:
            route = data['route']['trafast'][0]
            distance = route['summary']['distance']  # 거리 (미터)
            return distance
        else:
            logging.error(f"Error in route response: {data['message']}")
            return None
    else:
        logging.error(f"Error {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    # 임의로 설정한 두 지점 (경도, 위도)
    start_longitude = 126.9742286
    start_latitude = 37.5736565
    goal_longitude = 126.9798499
    goal_latitude = 37.570464
    
    start_coordinates = f"{start_longitude},{start_latitude}"
    goal_coordinates = f"{goal_longitude},{goal_latitude}"
    
    distance = get_distance(start_coordinates, goal_coordinates)
    
    if distance is not None:
        print(f"Distance from start to goal: {distance} meters")
    else:
        print("Failed to get distance between start and goal")
