# common/constants.py

# --- CẤU HÌNH MẠNG (NETWORK) ---
SERVER_HOST = '127.0.0.1'  # Localhost để dev. Đổi IP khi đưa lên mạng lan/internet.
SERVER_PORT = 5050
HEADER_LENGTH = 4          # Số byte dùng để lưu độ dài gói tin
FORMAT = 'utf-8'

# --- CẤU HÌNH GAME (BOARD & RULES) ---
BOARD_ROWS = 15
BOARD_COLS = 15
WIN_CONDITION = 5          # 5 nước liên tiếp để thắng
TURN_TIME_LIMIT = 30       # 30 giây mỗi lượt

# --- TRẠNG THÁI NGƯỜI CHƠI (USER STATUS) ---
STATUS_OFFLINE = "OFFLINE"
STATUS_ONLINE = "ONLINE"
STATUS_PLAYING = "PLAYING"

# --- KÝ HIỆU BÀN CỜ ---
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2