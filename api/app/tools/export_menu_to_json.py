import json
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Menu

def export_menu_to_compact_json():
    db: Session = SessionLocal()
    
    try:
        menus = db.query(Menu.store_id, Menu.menu).all()
        
        menu_dict = {}
        for menu in menus:
            store_id_str = str(menu.store_id)
            if store_id_str not in menu_dict:
                menu_dict[store_id_str] = []
            menu_dict[store_id_str].append(menu.menu)
        
        # JSON 파일로 저장
        with open('menu_data_compact.json', 'w', encoding='utf-8') as json_file:
            json.dump(menu_dict, json_file, ensure_ascii=False, separators=(',', ':'))
        
        print("Menu data has been successfully exported to menu_data_compact.json.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    export_menu_to_compact_json()