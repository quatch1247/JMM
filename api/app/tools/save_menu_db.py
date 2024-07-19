import json
import logging
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import StoresWithinRange, Menu

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data_to_db(data):
    db = SessionLocal()
    try:
        for entry in data:
            store_id = entry['store_id']
            for menu_name, price in entry['menu'].items():
                menu_item = Menu(store_id=store_id, menu=menu_name, price=price)
                db.add(menu_item)
        db.commit()
    except Exception as e:
        logging.error(f"Error saving data to DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    json_data = load_json_data("/Users/igeon/Desktop/Projects/JMM/parsed_data.json")
    save_data_to_db(json_data)
