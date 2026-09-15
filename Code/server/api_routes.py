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


def handle_find_match(client_socket, request_data, server_instance): #Xử lý yêu cầu tìm trận đấu từ client, thêm socket của client vào hàng đợi tìm trận và bắt đầu trận đấu nếu có đủ người chơi
    with match_lock:
        if client_socket not in match_queue:
            match_queue.append(client_socket)

        if len(match_queue) >= 2:
            sock_x = match_queue.pop(0)
            sock_o = match_queue.pop(0)

            user_x = server_instance.clients[sock_x]
            user_o = server_instance.clients[sock_o]

            match_id = str(uuid.uuid4())
            active_matches[match_id] = {
                "game": CaroGame(),
                "sock_x": sock_x,
                "sock_o": sock_o,
                "user_x_id": user_x["user_id"],
                "user_o_id": user_o["user_id"],
                "last_move_time": time.time()  # Ghi nhận thời điểm bắt đầu lượt
            }

            send_message(sock_x, {
                "action": "match_start",
                "match_id": match_id,
                "my_symbol": PLAYER_X,
                "opponent_name": user_o["username"]
            })

            send_message(sock_o, {
                "action": "match_start",
                "match_id": match_id,
                "my_symbol": PLAYER_O,
                "opponent_name": user_x["username"]
            })

    return None

def handle_make_move(client_socket, request_data, server_instance): #Xử lý yêu cầu đi nước từ client, xác nhận nước đi hợp lệ và gửi thông tin nước đi đến đối thủ
    match_id = request_data.get("match_id")
    row = request_data.get("row")
    col = request_data.get("col")

    with match_lock:
        match = active_matches.get(match_id)
        if not match:
            return None

        game = match["game"]
        sock_x = match["sock_x"]
        sock_o = match["sock_o"]

        player_symbol = PLAYER_X if client_socket == sock_x else PLAYER_O

        success, msg = game.make_move(row, col, player_symbol)
        if not success:
            return None
        match["last_move_time"] = time.time()# Cập nhật lại thời gian vừa đánh nước mới
        move_broadcast = {
                    "action": "move_made",
                    "row": row,
                    "col": col,
                    "symbol": player_symbol,
                    "next_turn": game.current_turn
                }
        send_message(sock_x, move_broadcast)# Gửi thông tin nước đi đến cả hai người chơi
        send_message(sock_o, move_broadcast)# Gửi thông tin nước đi đến cả hai người chơi
        
        if game.winner or game.is_draw:# Nếu có người thắng hoặc hòa, kết thúc trận đấu
            _finish_match(match_id, game.winner, game.is_draw, reason="normal")
            return None
def check_timeouts():# Kiểm tra hết giờ cho các trận đấu đang diễn ra
    while True:
        time.sleep(1)
        with match_lock:
            now = time.time()
            # Copy keys để tránh thay đổi dict khi đang lặp
            for match_id in list(active_matches.keys()):
                match = active_matches.get(match_id)
                if not match:
                    continue

                game = match["game"]
                # Nếu quá thời gian quy định (cộng 1s dung sai mạng)
                if now - match["last_move_time"] > (TURN_TIME_LIMIT + 1):
                    # Người hết giờ sẽ bị THUA -> Người kia THẮNG
                    timeout_winner = PLAYER_O if game.current_turn == PLAYER_X else PLAYER_X
                    print(f"[TIMEOUT] Trận {match_id} kết thúc do hết giờ lượt đi!")
                    _finish_match(match_id, winner_symbol=timeout_winner, is_draw=False, reason="timeout")

# Khởi chạy luồng kiểm tra hết giờ (Daemon Thread)
timeout_thread = threading.Thread(target=check_timeouts, daemon=True)
timeout_thread.start()

def _finish_match(match_id, winner_symbol, is_draw, reason="normal"):
    """Dọn dẹp trận đấu và cập nhật CSDL"""
    match = active_matches.get(match_id)
    if not match:
        return

    sock_x = match["sock_x"]
    sock_o = match["sock_o"]
    
    winner_id = None
    if winner_symbol == PLAYER_X:
        winner_id = match["user_x_id"]
    elif winner_symbol == PLAYER_O:
        winner_id = match["user_o_id"]

    db = SessionLocal()
    try:
        new_match = Match(
            player_x_id=match["user_x_id"],
            player_o_id=match["user_o_id"],
            winner_id=winner_id
        )
        db.add(new_match)

        user_x = db.query(User).filter(User.id == match["user_x_id"]).first()
        user_o = db.query(User).filter(User.id == match["user_o_id"]).first()

        if user_x and user_o:
            user_x.matches_played += 1
            user_o.matches_played += 1

            if winner_symbol == PLAYER_X:
                user_x.matches_won += 1
                user_x.elo += 15
                user_o.elo = max(0, user_o.elo - 10)
            elif winner_symbol == PLAYER_O:
                user_o.matches_won += 1
                user_o.elo += 15
                user_x.elo = max(0, user_x.elo - 10)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB ERROR] Lỗi lưu trận: {e}")
    finally:
        db.close()

    end_payload = {
        "action": "game_over",
        "winner_symbol": winner_symbol,
        "is_draw": is_draw,
        "reason": reason
    }
    send_message(sock_x, end_payload)
    send_message(sock_o, end_payload)

    if match_id in active_matches:
        del active_matches[match_id]

# Đăng ký Dispatcher
dispatcher.register("register", handle_register)
dispatcher.register("login", handle_login)
dispatcher.register("get_profile", handle_get_profile)
dispatcher.register("find_match", handle_find_match)
dispatcher.register("make_move", handle_make_move)   

