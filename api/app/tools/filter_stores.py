import logging
from sqlalchemy.orm import Session
from models import StoreInfo, StoresWithinRange
from database import SessionLocal, engine
from geopy.distance import geodesic

# 로깅 설정
logging.basicConfig(filename='store.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

def get_distance(start_coords, end_coords):
    distance_m = geodesic(start_coords, end_coords).meters  # 거리 (미터)
    logging.debug(f"Calculated geodesic distance: {distance_m} meters")
    return distance_m

def filter_and_store_stores():
    # 기준 좌표 설정 (위도, 경도)
    base_coordinates = (37.5736565, 126.9742286)
    
    # 데이터베이스 세션 생성
    db = SessionLocal()
    
    try:
        # store_info 테이블에서 데이터 가져오기
        stores = db.query(StoreInfo).all()
        
        for store in stores:
            store_coordinates = (store.coordinate_y, store.coordinate_x)  # (위도, 경도) 순서
            distance = get_distance(store_coordinates, base_coordinates)
            
            logging.debug(f"Store: {store.business_name}, Distance: {distance}")
            if distance <= 1000:  # 1000미터 이하인 경우에만 저장
                logging.info(f"Storing store: {store.business_name}, Distance: {distance}")
                new_store_within_range = StoresWithinRange(
                    business_name=store.business_name,
                    business_type=store.business_type,
                    address=store.address,
                    distance=distance
                )
                db.add(new_store_within_range)
                db.commit()
            else:
                logging.info(f"Skipping store: {store.business_name}, Distance: {distance}")
    except Exception as e:
        db.rollback()
        logging.error(f'Error processing stores: {str(e)}')
    finally:
        db.close()
    print("데이터베이스 업데이트 완료.")

if __name__ == "__main__":
    filter_and_store_stores()
