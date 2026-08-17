try:
    import requests
except ImportError: 
    requests = None


class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:5000/api", use_mock=False):
        self.base_url = base_url
        self.use_mock = use_mock
        self.token = None

    def login(self, username, password):
        """1. Đăng nhập tài khoản"""
        if not username or not password:
            return False, "Vui lòng điền đầy đủ thông tin!", None

        if self.use_mock:
            if username in ["vi_user", "admin"] and password == "123456":
                self.token = "fake-jwt-token-vi-123"
                user_info = {"username": username, "elo": 1200, "win": 10, "loss": 2, "token": self.token}
                return True, "Đăng nhập thành công!", user_info
            return False, "Tài khoản hoặc mật khẩu không chính xác!", None

        try:
            response = requests.post(f"{self.base_url}/login", json={"username": username, "password": password}, timeout=5)
            data = response.json()
            if response.status_code == 200 and data.get("success"):
                self.token = data.get("token")
                return True, data.get("message", "Thành công"), data.get("user")
            return False, data.get("message", "Thất bại"), None
        except Exception as e:
            return False, f"Lỗi kết nối máy chủ: {str(e)}", None

    def register(self, username, password, email):
        """2. Đăng ký tài khoản mới"""
        if not username or not password or not email:
            return False, "Vui lòng không để trống ô nào!"

        if self.use_mock:
            if username == "admin":
                return False, "Tài khoản này đã tồn tại!"
            return True, "Đăng ký thành công! Hãy đăng nhập lại."

        try:
            response = requests.post(
                f"{self.base_url}/register", 
                json={"username": username, "password": password, "email": email}, 
                timeout=5
            )
            data = response.json()
            return data.get("success", False), data.get("message", "Lỗi không xác định")
        except Exception as e:
            return False, f"Lỗi kết nối máy chủ: {str(e)}"

    def get_leaderboard(self):
        """3. Lấy danh sách Bảng xếp hạng Elo (Top 10)"""
        if self.use_mock:
            return [
                {"rank": 1, "username": "CaoThuCaro", "elo": 1650, "win_rate": "85%"},
                {"rank": 2, "username": "vi_user", "elo": 1200, "win_rate": "83%"},
                {"rank": 3, "username": "Hai_Socket", "elo": 1150, "win_rate": "60%"},
                {"rank": 4, "username": "Hao_Database", "elo": 1080, "win_rate": "55%"},
            ]

        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.base_url}/leaderboard", headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except Exception:
            return []

    def get_match_history(self, username):
        """4. Lấy lịch sử đấu của người chơi"""
        if self.use_mock:
            return [
                {"match_id": "M01", "opponent": "Hai_Socket", "result": "Thắng", "elo_change": "+15"},
                {"match_id": "M02", "opponent": "CaoThuCaro", "result": "Thua", "elo_change": "-10"},
            ]

        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.base_url}/users/{username}/history", headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except Exception:
            return []

