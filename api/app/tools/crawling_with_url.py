from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def fetch_menu(url):
    # Selenium 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 크롬 드라이버 경로 설정
    chrome_driver_path = '/opt/homebrew/bin/chromedriver'  # 크롬 드라이버 경로 설정 필요
    service = Service(chrome_driver_path)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # URL에 접속
    driver.get(url)
    
    # "메뉴 더보기" 버튼 클릭
    try:
        # WebDriverWait을 사용하여 요소가 로드될 때까지 기다림
        wait = WebDriverWait(driver, 10)
        menu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#app-root > div > div > div > div:nth-child(5) > div")))
        menu_button.click()
        time.sleep(2)  # 페이지가 로드될 시간을 기다림
    except Exception as e:
        print(f"메뉴 더보기 버튼을 찾을 수 없습니다: {e}")
        driver.quit()
        return
    
    # 페이지 소스를 가져와서 BeautifulSoup로 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 메뉴 아이템을 찾기
    menu_items = soup.find_all('li', class_='gHmZ_')
    
    menus = []
    
    for item in menu_items:
        name_tag = item.find('a', class_='place_bluelink ihmWt')
        price_tag = item.find('div', class_='mkBm3').find('em')
        if name_tag and price_tag:
            name = name_tag.text.strip()
            price = price_tag.text.strip()
            menus.append({'name': name, 'price': price})
    
    driver.quit()
    
    # 추출한 메뉴 정보 출력
    for menu in menus:
        print(f"메뉴: {menu['name']}, 가격: {menu['price']}")

# 테스트 URL
test_url = "https://map.naver.com/p/search/%EC%A0%95%EC%9B%90%20%EB%8F%84%EB%A0%B4/place/1617993985?c=15.00,0,0,0,dh"
fetch_menu(test_url)
