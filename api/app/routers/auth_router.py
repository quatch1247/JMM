from fastapi import APIRouter, HTTPException, BackgroundTasks, status, Depends
from fastapi.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.auth.email_verification import send_email_verification_code
from app.auth.redis_client import redis_client
from app.database import SessionLocal
from app.models import User, RefreshToken
from app.auth.jwt import create_access_token, create_refresh_token
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

CODE_EXPIRATION_TIME = 300

class VerificationCodeInput(BaseModel):
    verification_code: str

class EmailInput(BaseModel):
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def send_verification_code_task(email: EmailStr):
    code = send_email_verification_code(email)
    if code is None:
        raise HTTPException(status_code=500, detail="인증 코드 전송에 실패하였습니다.")
    redis_client.setex(code, CODE_EXPIRATION_TIME, email)

@router.post("/send-verification-code")
async def send_verification_code(email: EmailStr, background_tasks: BackgroundTasks):
    try:
        db = SessionLocal()
        user_id = email.split('@')[0]

        existing_user = db.query(User).filter(User.user_id == user_id).first()
        if existing_user:
            return JSONResponse(
                status_code=status.HTTP_208_ALREADY_REPORTED,
                content={"message": "이미 인증된 사용자입니다."}
            )

        background_tasks.add_task(send_verification_code_task, email)
        return {"email": email, "message": "인증 코드가 전송되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/verify-code", response_model=TokenResponse)
async def verify_code(input: VerificationCodeInput, db: Session = Depends(get_db)):
    try:
        stored_email = redis_client.get(input.verification_code)
        if stored_email:
            if isinstance(stored_email, bytes):
                stored_email = stored_email.decode('utf-8')
            user_id = stored_email.split('@')[0]
            
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                new_user = User(user_id=user_id)
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                user = new_user
            
            access_token = create_access_token(data={"sub": user_id})
            refresh_token_str = str(uuid.uuid4())
            refresh_token = create_refresh_token(data={"sub": user_id})
            print("refresh_token : ", refresh_token)

            token_record = RefreshToken(
                user_id=user.user_id,
                token=refresh_token_str,
                expiry=datetime.utcnow() + timedelta(days=7)
            )
            db.add(token_record)
            db.commit()
            
            return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)
        
        raise HTTPException(status_code=400, detail="유효하지 않는 인증 코드입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    token_record = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_record or token_record.expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired refresh token")

    user = token_record.user
    access_token = create_access_token(data={"sub": user.user_id})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/resend-verification-code")
async def resend_verification_code(email: EmailStr, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        user_id = email.split('@')[0]
        user = db.query(User).filter(User.user_id == user_id).first()

        if user:
            db.query(RefreshToken).filter(RefreshToken.user_id == user.user_id).delete()
            db.delete(user)
            db.commit()

        background_tasks.add_task(send_verification_code_task, email)
        return {"email": email, "message": "새로운 인증 코드가 전송되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
