from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:////app/app/users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SwitchConnection(BaseModel):
    ip: str
    username: str
    password: str

class DisconnectedPort(BaseModel):
    port: str
    description: str
    vlan: str
    last_input: str
    input_packets: str
    output_packets: str
    usage_percentage: float

class PoEStatus(BaseModel):
    switch_no: str
    available: str
    used: str
    free: str

class LowestUsage(BaseModel):
    interface: str
    usage_percentage: float

class SwitchResponse(BaseModel):
    hostname: str
    uptime: str
    disconnected_ports: List[DisconnectedPort]
    poe_status: Optional[List[PoEStatus]] = None
    lowest_usage_interface: Optional[LowestUsage] = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)