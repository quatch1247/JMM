import logging
from sqlalchemy.orm import Session
from models import StoreInfo
from database import SessionLocal
from geopy.distance import geodesic
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

# 로깅 설정
logging.basicConfig(filename='store.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

def get_walking_distance(start_address, end_address):
    # Selenium 웹드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저가 열리지 않도록 설정
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        # 네이버 지도 페이지 열기
        driver.get("https://map.naver.com/v5/directions/-/-/-/walk")
        time.sleep(5)  # 페이지 로딩 대기

        # 도보 탭 선택
        walk_tab_button = driver.find_element(By.XPATH, "//button[span[text()='도보']]")
        walk_tab_button.click()
        time.sleep(1)

        # 출발지 입력
        start_input = driver.find_element(By.CSS_SELECTOR, "input.input_search")
        start_input.clear()
        start_input.send_keys(start_address)
        time.sleep(1)

        # 도착지 입력
        end_input = driver.find_element(By.CSS_SELECTOR, "input.input_search")
        end_input.clear()
        end_input.send_keys(end_address)
        time.sleep(1)

        # 길찾기 버튼 클릭
        search_button = driver.find_element(By.XPATH, "//button[span[text()='길찾기']]")
        search_button.click()
        time.sleep(5)  # 결과 로딩 대기

        # 도보 경로 정보 추출
        walk_info_div = driver.find_element(By.CSS_SELECTOR, 'div.direction_top_area')
        walk_info = walk_info_div.find_element(By.CSS_SELECTOR, 'em.walk_direction_option_label').text
        if "가장 빠른" in walk_info:
            minutes = walk_info_div.find_element(By.CSS_SELECTOR, 'strong.sc-cdjj58 span.item_value').text
            meters = walk_info_div.find_elements(By.CSS_SELECTOR, 'span.walk_direction_info span.walk_direction_value')[0].text
            steps = walk_info_div.find_elements(By.CSS_SELECTOR, 'span.walk_direction_info span.walk_direction_value')[1].text
            print(f"가장 빠른 경로: {minutes}분, {meters}m, {steps}걸음")
            return minutes, meters, steps
    except Exception as e:
        logging.error(f'Error retrieving walking distance: {str(e)}')
        return None, None, None
    finally:
        driver.quit()

def filter_and_store_stores():
    # 기준 좌표 설정 (위도, 경도)
    base_coordinates = (37.5736565, 126.9742286)
    
    # 데이터베이스 세션 생성
    db = SessionLocal()
    
    try:
        # store_info 테이블에서 데이터 가져오기
        stores = db.query(StoreInfo).all()
        
        for store in stores:
            logging.debug(f"Store: {store.business_name}, Address: {store.address}")
            minutes, meters, steps = get_walking_distance("도렴빌딩", store.address)
            if minutes and meters and steps:
                print(f"{store.business_name}까지 도보 경로: {minutes}분, {meters}m, {steps}걸음")
            else:
                print(f"{store.business_name}까지 도보 경로 정보를 가져오지 못했습니다.")
    except Exception as e:
        db.rollback()
        logging.error(f'Error processing stores: {str(e)}')
    finally:
        db.close()
    print("데이터 확인 완료.")

if __name__ == "__main__":
    filter_and_store_stores()
