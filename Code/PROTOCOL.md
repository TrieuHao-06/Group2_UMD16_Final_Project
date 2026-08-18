# 📡 GIAO THỨC TRUYỀN THÔNG (SOCKET PROTOCOL) - GAME CARO ONLINE

> **Giải thích chung:** Tài liệu này quy định chuẩn định dạng dữ liệu truyền nhận qua TCP Socket giữa Client (CustomTkinter/Pygame) và Server (Python Socket). File này giúp Backend (Hải) và Frontend (Vĩ, Sơn Hào, Nga) kết nối chuẩn xác, không bị lệch tên hàm hay sai kiểu dữ liệu.

---

## 1. Quy Chuẩn Đóng Gói Dữ Liệu (TCP Framing)
> **Giải thích:** TCP là dạng dòng chảy dữ liệu (Stream). Nếu gửi liên tục, nhiều gói tin JSON sẽ bị dính liền vào nhau (dính gói) hoặc bị cắt đôi (xé gói). Vì vậy, Server và Client bắt buộc phải chèn thêm **4 bytes Header** ở đầu mỗi gói tin để thông báo chính xác độ dài của dữ liệu JSON phía sau.

* **Header:** 4 bytes Unsigned Integer (Big-endian) quy định độ dài của Payload.
* **Payload:** Chuỗi định dạng JSON mã hóa theo chuẩn `UTF-8`.
* **Cấu trúc gói tin tổng quát:**

```json
{
  "action": "TÊN_SỰ_KIỆN",
  "payload": { ... }
}

{
  "action": "AUTHENTICATE",
  "payload": {
    "user_id": 12,
    "username": "haipho2026",
    "token": "jwt_session_token_xyz"
  }
}

{
  "event": "AUTH_SUCCESS",
  "payload": {
    "message": "Xác thực Socket thành công"
  }
}

{
  "action": "CREATE_ROOM",
  "payload": {
    "room_name": "Phòng của Hải"
  }
}

{
  "event": "ROOM_CREATED",
  "payload": {
    "room_id": "ROOM_101",
    "symbol": "X"
  }
}

{
  "action": "JOIN_ROOM",
  "payload": {
    "room_id": "ROOM_101"
  }
}

{
  "event": "START_GAME",
  "payload": {
    "room_id": "ROOM_101",
    "player_x": "haipho2026",
    "player_o": "sonhao2026",
    "your_symbol": "X",
    "current_turn": "X",
    "turn_time": 30
  }
}

{
  "action": "MAKE_MOVE",
  "payload": {
    "room_id": "ROOM_101",
    "x": 7,
    "y": 7,
    "symbol": "X"
  }
}

{
  "event": "GAME_UPDATE",
  "payload": {
    "last_move": {"x": 7, "y": 7, "symbol": "X"},
    "next_turn": "O",
    "remaining_time": 30
  }
}

{
  "action": "SURRENDER",
  "payload": {
    "room_id": "ROOM_101"
  }
}

{
  "event": "GAME_OVER",
  "payload": {
    "winner_symbol": "X",
    "winner_username": "haipho2026",
    "reason": "FIVE_IN_A_ROW",
    "elo_change": {
      "haipho2026": 15,
      "sonhao2026": -15
    }
  }
}

{
  "action": "JOIN_SPECTATE",
  "payload": {
    "room_id": "ROOM_101"
  }
}

{
"event": "SPECTATE_INIT",
  "payload": {
    "room_id": "ROOM_101",
    "board_state": [
      ["", "", ""],
      ["", "X", ""],
      ["", "", "O"]
    ],
    "player_x": "haipho2026",
    "player_o": "sonhao2026",
    "current_turn": "O"
  }
}

{
  "action": "RECONNECT",
  "payload": {
    "user_id": 12,
    "room_id": "ROOM_101"
  }
}

{
  "event": "RECONNECT_SUCCESS",
  "payload": {
    "board_state": [],
    "current_turn": "X",
    "remaining_time": 18
  }
}
