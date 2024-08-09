import os
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Image

def insert_image_if_not_exists(store_id, image_path):
    db = SessionLocal()
    try:
        existing_image = db.query(Image).filter_by(store_id=store_id).first()
        if existing_image:
            print(f"Image for store_id {store_id} already exists. Skipping...")
            return

        with open(image_path, 'rb') as file:
            binary_data = file.read()

        new_image = Image(store_id=store_id, image=binary_data)
        db.add(new_image)
        db.commit()
        print(f"Inserted image for store_id {store_id}.")

    except Exception as e:
        print(f"Failed to insert image for store_id {store_id}. Error: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    image_folder = '/Users/igeon/Desktop/Projects/JMM/api/img'

    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpeg', '.jpg', '.png')):
            image_path = os.path.join(image_folder, filename)
            try:
                store_id = int(os.path.splitext(filename)[0])
                insert_image_if_not_exists(store_id, image_path)
            except ValueError:
                print(f"Skipping {filename}, as it does not contain a valid store_id.")

if __name__ == "__main__":
    main()
