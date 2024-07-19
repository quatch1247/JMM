import os
from sqlalchemy.orm import Session
from models import StoresWithinRange
from database import SessionLocal, engine

# 디렉토리 생성 함수
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 비즈니스 이름별로 빈 텍스트 파일을 생성하는 함수
def export_empty_files():
    # 세션 생성
    db = SessionLocal()

    try:
        # 디렉토리 생성
        output_directory = 'business_files'
        create_directory(output_directory)

        # 고유한 비즈니스 이름을 가져옴
        business_names = db.query(StoresWithinRange.business_name).distinct().all()

        # 각 비즈니스 이름에 대한 빈 파일 생성
        for name_tuple in business_names:
            business_name = name_tuple[0]
            file_path = os.path.join(output_directory, f"{business_name}.txt")

            # 빈 파일 생성
            with open(file_path, 'w', encoding='utf-8') as file:
                pass

            print(f"{file_path} created.")

    finally:
        # 세션 종료
        db.close()

# 파일 내용으로 raw_description 컬럼을 업데이트하는 함수
def update_raw_description():
    db = SessionLocal()

    try:
        directory = 'business_files'
        files = os.listdir(directory)

        for file_name in files:
            business_name, _ = os.path.splitext(file_name)
            file_path = os.path.join(directory, file_name)

            # 파일 내용을 읽어옴
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            # 데이터베이스 업데이트
            db.query(StoresWithinRange).filter(StoresWithinRange.business_name == business_name).update({"raw_description": content})
            print(f"Updated {business_name} with content from {file_name}")

        # 변경사항 커밋
        db.commit()

    finally:
        # 세션 종료
        db.close()

# URL을 저장할 수 있는 빈 텍스트 파일을 생성하는 함수
def export_empty_url_files():
    # 세션 생성
    db = SessionLocal()

    try:
        # 디렉토리 생성
        output_directory = 'url_files'
        create_directory(output_directory)

        # 고유한 비즈니스 이름을 가져옴
        business_names = db.query(StoresWithinRange.business_name).distinct().all()

        # 각 비즈니스 이름에 대한 빈 파일 생성
        for name_tuple in business_names:
            business_name = name_tuple[0]
            file_path = os.path.join(output_directory, f"{business_name}.txt")

            # 파일이 이미 존재하는지 확인하고, 존재하지 않을 때만 빈 파일 생성
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    pass

                print(f"{file_path} created.")
            else:
                print(f"{file_path} already exists, skipping.")

    finally:
        # 세션 종료
        db.close()

# 파일 내용으로 url 컬럼을 업데이트하는 함수
def update_url():
    db = SessionLocal()

    try:
        directory = 'url_files'
        files = os.listdir(directory)

        for file_name in files:
            business_name, _ = os.path.splitext(file_name)
            file_path = os.path.join(directory, file_name)

            # 파일 내용을 읽어옴
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()

            # 데이터베이스 업데이트
            db.query(StoresWithinRange).filter(StoresWithinRange.business_name == business_name).update({"url": content})
            print(f"Updated {business_name} with URL from {file_name}")

        # 변경사항 커밋
        db.commit()

    finally:
        # 세션 종료
        db.close()

if __name__ == "__main__":
    # export_empty_files()
    update_raw_description()
    # export_empty_url_files()
    # update_url()
