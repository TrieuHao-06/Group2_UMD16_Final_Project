
import bcrypt
import jwt
import datetime
import os

# Secret key cho JWT (Trong thực tế nên đặt trong file .env và không push lên Github)
SECRET_KEY = os.environ.get("SECRET_KEY", "caro_game_secret_key_15x15")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7 # Token có thời hạn 7 ngày

def hash_password(password: str) -> str:
    """
    Mã hóa mật khẩu người dùng bằng bcrypt.
    Hàm này được gọi khi người dùng Đăng ký (Register).
    """
    # Tạo salt ngẫu nhiên
    salt = bcrypt.gensalt()
    # Mã hóa password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu nhập vào có khớp với hash trong Database không.
    Hàm này được gọi khi người dùng Đăng nhập (Login).
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def generate_session_token(user_id: int, username: str) -> str:
    """
    Cấp phát Session Token (JWT) cho phiên đăng nhập.
    Trả về chuỗi Token để Client lưu trữ và gửi kèm trong các request cần xác thực.
    """
    expire_time = datetime.datetime.utcnow() + datetime.timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expire_time,
        "iat": datetime.datetime.utcnow()
    }
    # Tạo token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_session_token(token: str) -> dict:
    """
    Xác thực Session Token.
    Trả về payload (chứa user_id, username) nếu hợp lệ.
    Trả về None nếu token đã hết hạn hoặc không hợp lệ.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print(f"Token đã hết hạn.")
        return None
    except jwt.InvalidTokenError:
        print(f"Token không hợp lệ.")
        return None