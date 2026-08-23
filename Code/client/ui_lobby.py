import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from client.api_client import ApiClient
except ImportError:
    from api_client import ApiClient

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LobbyFrame(ctk.CTkFrame):
    def __init__(self, master, api_client: ApiClient, user_data: dict, on_logout_callback, on_start_game_callback):
        super().__init__(master, fg_color="transparent")
        self.api_client = api_client
        self.user_data = user_data or {"username": "Guest", "elo": 1200, "win": 0, "loss": 0}
        self.on_logout = on_logout_callback
        self.on_start_game = on_start_game_callback

        self.init_ui()

    def init_ui(self):
        # ---------------------------------------------------------
        # 1. thanh TOP BAR (Thanh công cụ trên cùng)
        # ---------------------------------------------------------
        self.top_bar = ctk.CTkFrame(self, corner_radius=12, fg_color="#1E1E1E", height=60)
        self.top_bar.pack(fill="x", padx=15, pady=(15, 10))

        # Logo / Title
        self.logo_label = ctk.CTkLabel(
            self.top_bar, 
            text="🎮 CARO MASTER LOBBY", 
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color="#3B8ED0"
        )
        self.logo_label.pack(side="left", padx=20)

        # Nút Đăng xuất
        self.btn_logout = ctk.CTkButton(
            self.top_bar, 
            text="Đăng xuất", 
            width=90, 
            height=32,
            fg_color="#D9534F", 
            hover_color="#C9302C",
            command=self.on_logout
        )
        self.btn_logout.pack(side="right", padx=15)

        # ---------------------------------------------------------
        # 2. KHUNG NỘI DUNG CHÍNH (Chi làm 2 cột Trái / Phải)
        # ---------------------------------------------------------
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=5)

        # CỘT TRÁI: User Card + Danh sách Phòng / Online
        self.left_column = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # CỘT PHẢI: Bảng Xếp Hạng (BXH Elo)
        self.right_column = ctk.CTkFrame(self.main_container, fg_color="transparent", width=320)
        self.right_column.pack(side="right", fill="both", padx=(10, 0))

        self.setup_user_card()
        self.setup_room_list()
        self.setup_leaderboard()

    # ---------------------------------------------------------
    # CỘT TRÁI - PART 1: CARD THÔNG TIN CÁ NHÂN
    # ---------------------------------------------------------
    def setup_user_card(self):
        self.user_card = ctk.CTkFrame(self.left_column, corner_radius=12, fg_color="#1E1E1E")
        self.user_card.pack(fill="x", pady=(0, 10), ipady=10)

        username = self.user_data.get("username", "Unknown")
        elo = self.user_data.get("elo", 1200)
        win = self.user_data.get("win", 0)
        loss = self.user_data.get("loss", 0)

        lbl_user = ctk.CTkLabel(
            self.user_card, 
            text=f"👤 {username}", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_user.pack(anchor="w", padx=20, pady=(10, 2))

        lbl_stats = ctk.CTkLabel(
            self.user_card, 
            text=f"⭐ Elo: {elo}  |  🏆 Thắng: {win}  |  ❌ Thua: {loss}", 
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        lbl_stats.pack(anchor="w", padx=20)

    # ---------------------------------------------------------
    # CỘT TRÁI - PART 2: DANH SÁCH NGƯỜI CHƠI / TÌM TRẬN
    # ---------------------------------------------------------
    def setup_room_list(self):
        self.room_frame = ctk.CTkFrame(self.left_column, corner_radius=12, fg_color="#1E1E1E")
        self.room_frame.pack(fill="both", expand=True, ipady=10)

        header = ctk.CTkLabel(
            self.room_frame, 
            text="🟢 Người chơi Trực tuyến / Sảnh chờ", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(anchor="w", padx=15, pady=12)

        # Danh sách cuộc cuộn Scrollable Frame
        self.scroll_players = ctk.CTkScrollableFrame(self.room_frame, fg_color="#141414", corner_radius=8)
        self.scroll_players.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Thanh nút bấm hành động
        self.action_box = ctk.CTkFrame(self.room_frame, fg_color="transparent")
        self.action_box.pack(fill="x", padx=15, pady=5)

        self.btn_refresh = ctk.CTkButton(
            self.action_box, text="🔄 Làm mới", width=110, height=36, command=self.load_online_players
        )
        self.btn_refresh.pack(side="left")

        self.btn_find_match = ctk.CTkButton(
            self.action_box, 
            text="⚔️ TÌM TRẬN NHANH", 
            height=36, 
            font=ctk.CTkFont(weight="bold"),
            command=self.handle_quick_match
        )
        self.btn_find_match.pack(side="right", fill="x", expand=True, padx=(10, 0))

        self.load_online_players()

    def load_online_players(self):
        # Clear danh sách cũ
        for widget in self.scroll_players.winfo_children():
            widget.destroy()

        # Dữ liệu giả lập người chơi online
        online_players = [
            {"username": "Hai_Socket", "elo": 1150, "status": "Sảnh chờ"},
            {"username": "Hao_Database", "elo": 1080, "status": "Sảnh chờ"},
            {"username": "CaoThuCaro", "elo": 1650, "status": "Đang chơi"},
            {"username": "Nga_UIUX", "elo": 1300, "status": "Sảnh chờ"},
        ]

        for player in online_players:
            item = ctk.CTkFrame(self.scroll_players, fg_color="#252525", corner_radius=8)
            item.pack(fill="x", pady=4, padx=5)

            p_info = ctk.CTkLabel(
                item, 
                text=f"{player['username']} ({player['elo']} Elo)", 
                font=ctk.CTkFont(size=13, weight="bold")
            )
            p_info.pack(side="left", padx=12, pady=8)

            if player['status'] == "Sảnh chờ":
                btn_challenge = ctk.CTkButton(
                    item, 
                    text="Thách đấu", 
                    width=85, 
                    height=28, 
                    font=ctk.CTkFont(size=12),
                    command=lambda p=player['username']: self.handle_challenge(p)
                )
                btn_challenge.pack(side="right", padx=10)
            else:
                lbl_status = ctk.CTkLabel(item, text="Đang chơi", text_color="gray", font=ctk.CTkFont(size=12))
                lbl_status.pack(side="right", padx=15)

    # ---------------------------------------------------------
    # CỘT PHẢI: BẢNG XẾP HẠNG TOP ELO
    # ---------------------------------------------------------
    def setup_leaderboard(self):
        self.bxh_frame = ctk.CTkFrame(self.right_column, corner_radius=12, fg_color="#1E1E1E")
        self.bxh_frame.pack(fill="both", expand=True)

        header = ctk.CTkLabel(
            self.bxh_frame, 
            text="🏆 BẢNG XẾP HẠNG TOP ELO", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#FFD700" # Màu vàng kim
        )
        header.pack(pady=12)

        self.scroll_bxh = ctk.CTkScrollableFrame(self.bxh_frame, fg_color="#141414", corner_radius=8)
        self.scroll_bxh.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.load_leaderboard()

    def load_leaderboard(self):
        for widget in self.scroll_bxh.winfo_children():
            widget.destroy()

        bxh_data = self.api_client.get_leaderboard()

        for item in bxh_data:
            rank = item.get("rank", "-")
            name = item.get("username", "-")
            elo = item.get("elo", "-")

            row = ctk.CTkFrame(self.scroll_bxh, fg_color="#212121", corner_radius=6)
            row.pack(fill="x", pady=3, padx=2)

            rank_color = "#FFD700" if rank == 1 else ("#C0C0C0" if rank == 2 else ("#CD7F32" if rank == 3 else "white"))
            
            lbl_rank = ctk.CTkLabel(row, text=f"#{rank}", width=30, text_color=rank_color, font=ctk.CTkFont(weight="bold"))
            lbl_rank.pack(side="left", padx=(5, 0))

            lbl_name = ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=12))
            lbl_name.pack(side="left", padx=10)

            lbl_elo = ctk.CTkLabel(row, text=f"{elo} Elo", text_color="#3B8ED0", font=ctk.CTkFont(size=12, weight="bold"))
            lbl_elo.pack(side="right", padx=10)

    # ---------------------------------------------------------
    # XỬ LÝ SỰ KIỆN NÚT BẤM
    # ---------------------------------------------------------
    def handle_challenge(self, opponent_name):
        messagebox.showinfo("Thách đấu", f"Đã gửi lời mời thách đấu tới: {opponent_name}!\nĐang chờ đối phương phản hồi...")

    def handle_quick_match(self):
        messagebox.showinfo("Tìm trận", "Đang tự động ghép trận với đối thủ cùng Elo...")
        # Gọi callback chuyển sang bàn cờ Pygame của Sơn Hào
        self.on_start_game("ROOM_QUICK_MATCH")


# =========================================================
# CHẠY TEST ĐỘC LẬP MÀN HÌNH SẢNH
# =========================================================
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Caro Master - Sảnh Game")
    app.geometry("850x580")
    app.configure(fg_color="#0F0F0F")

    api = ApiClient(use_mock=True)
    fake_user = {"username": "vi_user", "elo": 1200, "win": 12, "loss": 3}

    def mock_logout():
        messagebox.showinfo("Logout", "Đăng xuất thành công!")

    def mock_start_game(room_id):
        messagebox.showinfo("Start Game", f"Chuyển sang Bàn cờ Pygame: {room_id}")

    lobby = LobbyFrame(app, api, fake_user, on_logout_callback=mock_logout, on_start_game_callback=mock_start_game)
    lobby.pack(fill="both", expand=True)

    app.mainloop()