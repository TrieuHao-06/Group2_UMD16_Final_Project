# server/server.py
import socket
import threading
from common.constants import SERVER_HOST, SERVER_PORT
from common.network_utils import receive_message, send_message
from .dispatcher import dispatcher

class GameServer:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # SO_REUSEADDR giúp khởi động lại server ngay lập tức mà không bị lỗi "Port already in use"
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Quản lý danh sách client kết nối: {socket: {"user_id": None, "username": None}}
        self.clients = {}
        self.clients_lock = threading.Lock() # Khóa (Lock) để tránh xung đột khi nhiều luồng cùng thao tác

    def start(self):
        """Bật server và bắt đầu lắng nghe kết nối"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10) # Cho phép tối đa 10 người đợi kết nối cùng lúc
        print(f"[SERVER] Đã mở cổng! Đang lắng nghe tại {self.host}:{self.port}...")

        try:
            while True:
                # accept() sẽ chặn luồng chính cho đến khi có người mới kết nối
                client_socket, client_address = self.server_socket.accept()
                print(f"[NEW CONNECTION] {client_address} vừa kết nối.")
                
                with self.clients_lock:
                    self.clients[client_socket] = {"address": client_address, "user_id": None, "username": None}
                
                # Cấp ngay cho người này 1 luồng riêng (thread) để xử lý
                thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                thread.daemon = True # Thread tự đóng khi tắt Server chính
                thread.start()
                
        except KeyboardInterrupt:
            print("\n[SERVER] Đang tiến hành tắt server...")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        """Luồng chuyên trách nhận và gửi tin nhắn cho MỘT client"""
        try:
            while True:
                # 1. Nhận tin nhắn an toàn (đã bóc 4 byte header)
                request_data = receive_message(client_socket)
                
                # Nếu receive_message trả về None nghĩa là client đã ngắt kết nối
                if request_data is None:
                    break 
                
                # 2. Đẩy data cho Dispatcher xử lý logic
                response_data = dispatcher.dispatch(client_socket, request_data, self)
                
                # 3. Trả phản hồi lại cho Client (nếu có)
                if response_data:
                    send_message(client_socket, response_data)
                    
        except Exception as e:
            print(f"[CONNECTION WARNING] Lỗi với {client_address}: {e}")
        finally:
            self.disconnect_client(client_socket, client_address)

    def disconnect_client(self, client_socket, client_address):
        """Xóa thông tin dọn dẹp khi Client rời đi"""
        with self.clients_lock:
            if client_socket in self.clients:
                del self.clients[client_socket]
        client_socket.close()
        print(f"[DISCONNECT] {client_address} đã rời khỏi hệ thống.")