from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, LargeBinary
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), unique=True, index=True)

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('users.user_id'))
    token = Column(String(256), unique=True, index=True)
    expiry = Column(DateTime)
    user = relationship("User", back_populates="tokens")

User.tokens = relationship("RefreshToken", back_populates="user")

class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    division = Column(String(10))
    admin_code = Column(String(10), unique=True, index=True)
    level1 = Column(String(50))
    level2 = Column(String(50), nullable=True)
    level3 = Column(String(50), nullable=True)
    grid_x = Column(Integer)
    grid_y = Column(Integer)
    longitude_deg = Column(Integer)
    longitude_min = Column(Integer)
    longitude_sec = Column(Float)
    latitude_deg = Column(Integer)
    latitude_min = Column(Integer)
    latitude_sec = Column(Float)
    longitude_decimal = Column(Float)
    latitude_decimal = Column(Float)
    update_date = Column(DateTime, nullable=True)
    
class StoreInfo(Base):
    __tablename__ = 'store_info'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_name = Column(String(255))
    business_type = Column(String(255))
    address = Column(String(255))
    coordinate_x = Column(Float)
    coordinate_y = Column(Float)    

class StoresWithinRange(Base):
    __tablename__ = 'stores_within_range'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_name = Column(String(255))
    business_type = Column(String(255))
    address = Column(String(255))
    distance = Column(Float)
    url = Column(String(2048))
    is_in_company_building = Column(Boolean, default=False)
    ai_summarize = Column(String(2048))
    raw_description = Column(Text) 

class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer)
    menu = Column(String(255))
    price = Column(String(255))
    
class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    store_id = Column(Integer, nullable=False)
    image = Column(LargeBinary, nullable=True)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer)
    name = Column(String(255), unique=True)
