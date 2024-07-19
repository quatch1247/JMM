from database import SessionLocal
from models import StoreInfo
from pyproj import Proj, transform
from pyproj.exceptions import ProjError
import numpy as np

# 좌표 변환 함수 정의
def transform_coordinates(x_list, y_list):
    in_proj = Proj(init='epsg:2097')  # 입력 좌표계 (중부원점TM)
    out_proj = Proj(init='epsg:4326')  # 출력 좌표계 (WGS84)

    try:
        # 좌표 변환
        converted = transform(in_proj, out_proj, x_list, y_list)
        # 소수점 이하 6자리로 제한
        lon_list = np.round(converted[0], 6)
        lat_list = np.round(converted[1], 6)
        return lon_list, lat_list
    except ProjError as e:
        print(f"Error converting coordinates: {e}")
        return None, None

# 데이터베이스에서 모든 StoreInfo 레코드를 가져와서 변환 후 업데이트
def update_coordinates():
    session = SessionLocal()

    stores = session.query(StoreInfo).all()

    coordinate_x_list = []
    coordinate_y_list = []

    for store in stores:
        coordinate_x_list.append(store.coordinate_x)
        coordinate_y_list.append(store.coordinate_y)

    lon_list, lat_list = transform_coordinates(np.array(coordinate_x_list), np.array(coordinate_y_list))

    if lon_list is None or lat_list is None:
        print("Error occurred during coordinate transformation.")
        session.close()
        return

    for store, lon, lat in zip(stores, lon_list, lat_list):
        store.coordinate_x = lon
        store.coordinate_y = lat

    try:
        session.commit()
    except Exception as e:
        print(f"Error committing changes: {e}")
        session.rollback()
    finally:
        session.close()

# 변환 함수 호출 및 업데이트 실행
if __name__ == "__main__":
    update_coordinates()
