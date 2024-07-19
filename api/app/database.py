from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import get_settings

settings = get_settings()

DATABASE_URL = (
    f"mysql+pymysql://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    poolclass=QueuePool,
    pool_size=100,
    max_overflow=50
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    inspector = inspect(engine)
    for table_name in Base.metadata.tables:
        if not inspector.has_table(table_name):
            print(f"Creating table {table_name}")
            Base.metadata.tables[table_name].create(engine)
        else:
            print(f"Table {table_name} already exists")
    
    all_tables = inspector.get_table_names()
    print("Current tables in the database:")
    for table in all_tables:
        print(table)

def test_connection():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT VERSION()"))
        version = result.fetchone()
        print(f"Database connection successful. Database version: {version[0]}")
    except Exception as e:
        print(f"Database connection failed. Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
    create_tables()
