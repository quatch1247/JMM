import re
from sqlalchemy.orm import Session
from database import SessionLocal
from models import StoresWithinRange

# 정규식 패턴 정의
pattern = re.compile(r'\[(.*?)\]')

def process_ai_summarize(text):
    """ 주어진 텍스트에서 [] 안에 있는 내용을 '상세보기'로 대체 """
    return pattern.sub('[상세보기]', text)

def update_ai_summarize():
    # 데이터베이스 세션 생성
    db: Session = SessionLocal()
    try:
        # 모든 stores_within_range 레코드 가져오기
        records = db.query(StoresWithinRange).all()

        for record in records:
            ai_summarize = record.ai_summarize
            
            # ai_summarize 컬럼 변환
            if ai_summarize:
                new_ai_summarize = process_ai_summarize(ai_summarize)
                record.ai_summarize = new_ai_summarize

        # 변경사항 커밋
        db.commit()
        print("ai_summarize 컬럼이 성공적으로 업데이트되었습니다.")
    except Exception as e:
        db.rollback()
        print(f"업데이트 중 오류 발생: {e}")
    finally:
        db.close()

# if __name__ == "__main__":
#     update_ai_summarize()
