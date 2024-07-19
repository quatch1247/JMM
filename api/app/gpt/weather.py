import pandas as pd
import math
import json
import requests
from datetime import datetime, timedelta as td
from sqlalchemy.orm import sessionmaker
from app.models import Location
from app.database import SessionLocal, create_tables
from app.config import get_settings
from datetime import datetime, timedelta
import pytz

settings = get_settings()
serviceKey = settings.weather_api_key
print("@@@",serviceKey)

def save_excel_to_db(file_path):
    session = SessionLocal()
    
    df = pd.read_excel(file_path, sheet_name='최종 업데이트 파일_20240101')
    
    for _, row in df.iterrows():
        update_date = None
        if pd.notna(row['위치업데이트']):
            try:
                update_date_str = str(row['위치업데이트']).replace(",", "")
                update_date = datetime.strptime(update_date_str, '%Y%m%d')
            except ValueError as e:
                print(f"Error parsing date for row: {row['위치업데이트']}, error: {e}")

        location = Location(
            division=row['구분'] if pd.notna(row['구분']) else None,
            admin_code=row['행정구역코드'] if pd.notna(row['행정구역코드']) else None,
            level1=row['1단계'] if pd.notna(row['1단계']) else None,
            level2=row['2단계'] if pd.notna(row['2단계']) else None,
            level3=row['3단계'] if pd.notna(row['3단계']) else None,
            grid_x=row['격자 X'] if pd.notna(row['격자 X']) else None,
            grid_y=row['격자 Y'] if pd.notna(row['격자 Y']) else None,
            longitude_deg=row['경도(시)'] if pd.notna(row['경도(시)']) else None,
            longitude_min=row['경도(분)'] if pd.notna(row['경도(분)']) else None,
            longitude_sec=row['경도(초)'] if pd.notna(row['경도(초)']) else None,
            latitude_deg=row['위도(시)'] if pd.notna(row['위도(시)']) else None,
            latitude_min=row['위도(분)'] if pd.notna(row['위도(분)']) else None,
            latitude_sec=row['위도(초)'] if pd.notna(row['위도(초)']) else None,
            longitude_decimal=row['경도(초/100)'] if pd.notna(row['경도(초/100)']) else None,
            latitude_decimal=row['위도(초/100)'] if pd.notna(row['위도(초/100)']) else None,
            update_date=update_date
        )
        session.add(location)
    
    session.commit()
    session.close()
    
def latlon_to_grid(lat, lon):
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기준점 Y좌표(GRID)

    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)

    rs = {}
    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / (ra ** sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    rs['x'] = math.floor(ra * math.sin(theta) + XO + 0.5)
    rs['y'] = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

    return rs['x'], rs['y']

def deg_to_dir(deg):
    deg_code = {
        0: 'N', 360: 'N', 180: 'S', 270: 'W', 90: 'E', 22.5: 'NNE',
        45: 'NE', 67.5: 'ENE', 112.5: 'ESE', 135: 'SE', 157.5: 'SSE',
        202.5: 'SSW', 225: 'SW', 247.5: 'WSW', 292.5: 'WNW', 315: 'NW',
        337.5: 'NNW'
    }
    close_dir = ''
    min_abs = 360
    if deg not in deg_code.keys():
        for key in deg_code.keys():
            if abs(key - deg) < min_abs:
                min_abs = abs(key - deg)
                close_dir = deg_code[key]
    else:
        close_dir = deg_code[deg]
    return close_dir

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def get_closest_location(target_lat, target_lon):
    session = SessionLocal()
    try:
        locations = session.query(Location).all()
        closest_location = None
        min_distance = float('inf')
        for location in locations:
            distance = calculate_distance(target_lat, target_lon, location.latitude_decimal, location.longitude_decimal)
            if distance < min_distance:
                min_distance = distance
                closest_location = location
        return closest_location
    finally:
        session.close()

def weather_info(nx, ny):
    now = datetime.now()
    input_d = now - td(hours=1)
    input_date = input_d.strftime("%Y%m%d")
    input_time = input_d.strftime("%H%M")

    url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst?serviceKey={serviceKey}&numOfRows=60&pageNo=1&dataType=json&base_date={input_date}&base_time={input_time}&nx={nx}&ny={ny}"
    
    response = requests.get(url, verify=False)
    
    res = json.loads(response.text)

    informations = dict()
    for items in res['response']['body']['items']['item']:
        cate = items['category']
        fcstTime = items['fcstTime']
        fcstValue = items['fcstValue']
        if fcstTime not in informations:
            informations[fcstTime] = {}
        informations[fcstTime][cate] = fcstValue

    latest_time = max(informations.keys())
    return informations[latest_time], input_date, input_time

def print_weather_info(val, nx, ny, location):
    sky_code = {1: '맑음', 3: '구름많음', 4: '흐림'}
    pty_code = {0: '강수 없음', 1: '비', 2: '비/눈', 3: '눈', 5: '빗방울', 6: '진눈깨비', 7: '눈날림'}

    location_info = " ".join(filter(None, [location.level1, location.level2, location.level3]))

    now = datetime.now()
    current_date = now.strftime("%Y년 %m월 %d일")
    current_time = now.strftime("%H시 %M분")

    weather_report = f"{current_date} {current_time}에 {location_info} 지역({nx}, {ny})의 날씨는 "

    sky = val.get('SKY')
    if sky is not None:
        sky_description = sky_code.get(int(sky), '알 수 없음')
        weather_report += f"{sky_description}이며, "

    pty = val.get('PTY')
    if pty is not None:
        pty_description = pty_code.get(int(pty), '알 수 없음')
        weather_report += f"{pty_description}"
        rn1 = val.get('RN1')
        if rn1 and rn1 != '강수 없음':
            weather_report += f" (시간당 {rn1}mm), "

    t1h = val.get('T1H')
    if t1h is not None:
        temperature = float(t1h)
        weather_report += f"기온은 {temperature}℃, "

    reh = val.get('REH')
    if reh is not None:
        humidity = float(reh)
        weather_report += f"습도는 {humidity}%, "

    vec = val.get('VEC')
    wsd = val.get('WSD')
    if vec is not None and wsd is not None:
        wind_direction = deg_to_dir(float(vec))
        wind_speed = wsd
        weather_report += f"풍속은 {wind_direction} 방향으로 {wind_speed}m/s입니다."

    return weather_report.strip().rstrip(",")

def md_print_weather_info(val):
    sky_code = {1: '맑음', 3: '구름많음', 4: '흐림'}
    pty_code = {0: '강수 없음', 1: '비', 2: '비/눈', 3: '눈', 5: '빗방울', 6: '진눈깨비', 7: '눈날림'}

    now = datetime.now()
    current_time = now.strftime("%H시 %M분")

    weather_report = f"#### 종로구 도렴동 지역의 날씨 정보\n"

    sky = val.get('SKY')
    sky_description = sky_code.get(int(sky), '알 수 없음') if sky is not None else '알 수 없음'
    weather_report += f"- **날씨 상태**: `{sky_description}`\n"

    pty = val.get('PTY')
    pty_description = pty_code.get(int(pty), '알 수 없음') if pty is not None else '알 수 없음'
    rn1 = val.get('RN1', '0')
    if pty_description != '강수 없음':
        weather_report += f"- **강수량**: `시간당 {rn1}mm`\n"

    t1h = val.get('T1H')
    temperature = f"{float(t1h):.1f}°C" if t1h is not None else '알 수 없음'
    weather_report += f"- **기온**: `{temperature}`\n"
    
    reh = val.get('REH')
    humidity = f"{float(reh):.0f}%" if reh is not None else '알 수 없음'
    weather_report += f"- **습도**: `{humidity}`\n"

    return weather_report

def get_weather_info():
    try:
        target_lat = 37.573659250866065
        target_lon = 126.97385253462173
        now = datetime.now(pytz.timezone('Asia/Seoul'))
        base_date = now.strftime("%Y%m%d")
        base_time = (now - timedelta(hours=1)).strftime("%H%M")

        location = get_closest_location(target_lat, target_lon)

        if location:
            nx, ny = latlon_to_grid(location.latitude_decimal, location.longitude_decimal)

            latest_weather, base_date, base_time = weather_info(nx, ny)

            result = print_weather_info(latest_weather, nx, ny, location)
            return result
        else:
            return "해당 위도와 경도의 위치 정보가 데이터베이스에 없습니다."
    except Exception as e:
        return f"오류 발생: {str(e)}"

def md_get_weather_info():
    try:
        target_lat = 37.573659250866065
        target_lon = 126.97385253462173
        now = datetime.now(pytz.timezone('Asia/Seoul'))
        base_date = now.strftime("%Y%m%d")
        base_time = (now - timedelta(hours=1)).strftime("%H%M")

        location = get_closest_location(target_lat, target_lon)

        if location:
            nx, ny = latlon_to_grid(location.latitude_decimal, location.longitude_decimal)

            latest_weather, base_date, base_time = weather_info(nx, ny)

            result = md_print_weather_info(latest_weather)
            return result
        else:
            return "해당 위도와 경도의 위치 정보가 데이터베이스에 없습니다."
    except Exception as e:
        return f"오류 발생: {str(e)}"

if __name__ == "__main__":
    target_lat = 37.57384225497904
    target_lon = 126.97507309813098

    my_weather_info = get_weather_info()
    print(my_weather_info)