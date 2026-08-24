# server/dispatcher.py

class RequestDispatcher:
    def __init__(self):
        # Biến này lưu danh sách các "Hành động" và "Hàm xử lý" tương ứng
        self.handlers = {}

    def register(self, action, handler_function):
        """Đăng ký một hàm xử lý cho một hành động (action) cụ thể."""
        self.handlers[action] = handler_function

    def dispatch(self, client_socket, request_data, server_instance):
        """Phân phối gói tin đến đúng hàm xử lý dựa trên trường 'action'."""
        action = request_data.get("action")
        
        if not action:
            return {"status": "error", "message": "Thiếu trường 'action' trong request"}
        
        handler = self.handlers.get(action)
        if not handler:
            return {"status": "error", "message": f"Action '{action}' không được hỗ trợ"}
        
        # Gọi hàm xử lý và trả kết quả về cho client
        try:
            return handler(client_socket, request_data, server_instance)
        except Exception as e:
            print(f"[DISPATCHER ERROR] Lỗi tại action '{action}': {e}")
            return {"status": "error", "message": "Lỗi nội bộ Server"}

# Khởi tạo một đối tượng duy nhất (Singleton) để dùng chung trên toàn Server
dispatcher = RequestDispatcher()