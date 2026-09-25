# server/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "server", "caro_game.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Khởi tạo Engine kết nối (check_same_thread=False cần thiết cho SQLite trong môi trường đa luồng)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Tạo Session để tương tác với Database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Lớp Base để các Models kế thừa
Base = declarative_base()

def init_db():
    """Hàm này sẽ tạo tất cả các bảng vào CSDL nếu chưa có"""
    Base.metadata.create_all(bind=engine)
    print("[DATABASE] Đã khởi tạo Cơ sở dữ liệu thành công.")