# server/api_routes.py
import uuid
import time
import threading
from .dispatcher import dispatcher
from .database import SessionLocal
from .models import User, Match
from .auth import get_password_hash, verify_password
from .game_logic import CaroGame
from common.constants import PLAYER_X, PLAYER_O, TURN_TIME_LIMIT
from common.network_utils import send_message

match_queue = []         # Danh sách socket đang tìm trận
active_matches = {}      # Các trận đang diễn ra
match_lock = threading.Lock()

# --- AUTHENTICATION & PROFILE ---

def handle_register(client_socket, request_data, server_instance): #Tiếp nhận và xử lý yêu cầu tạo tài khoản người dùng mới từ client
    username = request_data.get("username")
    password = request_data.get("password")

    if not username or not password:
        return {"action": "register_response", "status": "error", "message": "Thiếu thông tin đăng ký."}

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return {"action": "register_response", "status": "error", "message": "Tên đăng nhập đã tồn tại."}

        hashed_password = get_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        db.add(new_user)
        db.commit()
        return {"action": "register_response", "status": "success", "message": "Đăng ký thành công!"}
    except Exception as e:
        db.rollback()
        return {"action": "register_response", "status": "error", "message": "Lỗi CSDL."}
    finally:
        db.close()


def handle_login(client_socket, request_data, server_instance): #Xử lý Đăng nhập
    username = request_data.get("username")
    password = request_data.get("password")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):
            return {"action": "login_response", "status": "error", "message": "Sai tài khoản hoặc mật khẩu."}

        with server_instance.clients_lock:
            server_instance.clients[client_socket]["user_id"] = user.id
            server_instance.clients[client_socket]["username"] = user.username

        return {
            "action": "login_response",
            "status": "success",
            "message": "Đăng nhập thành công!",
            "data": {
                "id": user.id,
                "username": user.username,
                "elo": user.elo,
                "matches_played": user.matches_played,
                "matches_won": user.matches_won
            }
        }
    finally:
        db.close()

def handle_get_profile(client_socket, request_data, server_instance): #Lấy thông tin hồ sơ người dùng từ cơ sở dữ liệu dựa trên user_id được lưu trong server_instance.clients
    """API giúp Client lấy lại thông tin Elo/Thắng thua mới nhất sau trận đấu"""
    user_info = server_instance.clients.get(client_socket)
    if not user_info or not user_info.get("user_id"):
        return {"action": "get_profile_response", "status": "error"}

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_info["user_id"]).first()
        if user:
            return {
                "action": "get_profile_response",
                "status": "success",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "elo": user.elo,
                    "matches_played": user.matches_played,
                    "matches_won": user.matches_won
                }
            }
    finally:
        db.close()