# server/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Lưu mật khẩu đã băm (hash)
    
    # Chỉ số xếp hạng
    elo = Column(Integer, default=1000)
    matches_played = Column(Integer, default=0)
    matches_won = Column(Integer, default=0)

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    player_x_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player_o_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True) # None nếu trận hòa
    played_at = Column(DateTime, default=datetime.utcnow)