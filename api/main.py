from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_router, hello_router, utils_router, recommendation_router
from app.database import create_tables
from app.models import User 

app = FastAPI()

@app.on_event("startup")
def on_startup():
    print("create_tables")
    create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(hello_router.router)
app.include_router(utils_router.router)
app.include_router(recommendation_router.router)