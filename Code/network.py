# client/network.py
import socket
import threading
from common.constants import SERVER_HOST, SERVER_PORT
from common.network_utils import send_message, receive_message

class NetworkClient:
    def __init__(self):
        self.sock = None
        self.is_connected = False
        self.response_callbacks = {} # Lưu callback xử lý response theo action

    def connect(self, host=SERVER_HOST, port=SERVER_PORT):
        """Kết nối tới Server TCP"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.is_connected = True
            
            # Chạy luồng đọc tin nhắn ngầm từ Server
            listen_thread = threading.Thread(target=self._listen_from_server, daemon=True)
            listen_thread.start()
            return True, "Kết nối thành công!"
        except Exception as e:
            self.is_connected = False
            return False, f"Không thể kết nối Server: {e}"

    def send(self, data):
        """Gửi gói tin JSON sang Server"""
        if self.is_connected and self.sock:
            try:
                send_message(self.sock, data)
            except Exception as e:
                print(f"[CLIENT NETWORK ERROR] Lỗi gửi tin: {e}")

    def register_callback(self, action, callback_function):
        """Đăng ký hàm hứng phản hồi từ Server cho từng action"""
        self.response_callbacks[action] = callback_function

    def _listen_from_server(self):
        """Luồng liên tục lắng nghe phản hồi từ Server"""
        while self.is_connected:
            response = receive_message(self.sock)
            if response is None:
                print("[CLIENT NETWORK] Đã ngắt kết nối với Server.")
                self.is_connected = False
                break
            
            action = response.get("action")
            if action in self.response_callbacks:
                # Gọi hàm callback đã đăng ký để cập nhật UI
                self.response_callbacks[action](response)

    def close(self):
        self.is_connected = False
        if self.sock:
            self.sock.close()