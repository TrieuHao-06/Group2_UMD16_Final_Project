import customtkinter as ctk
from tkinter import messagebox


class LobbyWindow(ctk.CTk):
    def __init__(self, username="Player"):
        super().__init__()

        # ==============================
        # CẤU HÌNH CỬA SỔ
        # ==============================
        self.title("Caro Online - Sảnh chính")
        self.geometry("900x650")
        self.resizable(False, False)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.username = username

        # ==============================
        # TIÊU ĐỀ
        # ==============================
        self.title_label = ctk.CTkLabel(
            self,
            text="CARO ONLINE",
            font=("Arial", 30, "bold")
        )
        self.title_label.pack(pady=(25, 5))

        self.welcome_label = ctk.CTkLabel(
            self,
            text=f"Xin chào, {self.username}!",
            font=("Arial", 16)
        )
        self.welcome_label.pack(pady=(0, 20))

        # ==============================
        # THÔNG TIN NGƯỜI CHƠI
        # ==============================
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=30, pady=10)

        self.elo_label = ctk.CTkLabel(
            self.info_frame,
            text="Elo: 1200",
            font=("Arial", 16, "bold")
        )
        self.elo_label.pack(side="left", padx=30, pady=15)

        self.win_label = ctk.CTkLabel(
            self.info_frame,
            text="Thắng: 0",
            font=("Arial", 14)
        )
        self.win_label.pack(side="left", padx=30)

        self.lose_label = ctk.CTkLabel(
            self.info_frame,
            text="Thua: 0",
            font=("Arial", 14)
        )
        self.lose_label.pack(side="left", padx=30)

        # ==============================
        # KHU VỰC CHÍNH
        # ==============================
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        # ==============================
        # NGƯỜI CHƠI ONLINE
        # ==============================
        self.online_frame = ctk.CTkFrame(self.main_frame)
        self.online_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(15, 7),
            pady=15
        )

        self.online_title = ctk.CTkLabel(
            self.online_frame,
            text="NGƯỜI CHƠI ONLINE",
            font=("Arial", 18, "bold")
        )
        self.online_title.pack(pady=15)

        # Danh sách người chơi mẫu
        players = [
            ("Player01", "1500"),
            ("Player02", "1400"),
            ("Player03", "1350"),
            ("Player04", "1280"),
            ("Player05", "1200")
        ]

        for player_name, elo in players:

            player_frame = ctk.CTkFrame(
                self.online_frame
            )
            player_frame.pack(
                fill="x",
                padx=15,
                pady=5
            )

            player_label = ctk.CTkLabel(
                player_frame,
                text=f"● {player_name}  |  Elo: {elo}",
                font=("Arial", 13)
            )
            player_label.pack(
                side="left",
                padx=10,
                pady=10
            )

            challenge_button = ctk.CTkButton(
                player_frame,
                text="THÁCH ĐẤU",
                width=100,
                command=lambda p=player_name:
                    self.send_challenge(p)
            )
            challenge_button.pack(
                side="right",
                padx=10
            )

        # ==============================
        # BẢNG XẾP HẠNG
        # ==============================
        self.ranking_frame = ctk.CTkFrame(self.main_frame)
        self.ranking_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(7, 15),
            pady=15
        )

        self.ranking_title = ctk.CTkLabel(
            self.ranking_frame,
            text="BẢNG XẾP HẠNG ELO",
            font=("Arial", 18, "bold")
        )
        self.ranking_title.pack(pady=15)

        ranking = [
            ("1.", "Player01", "1500"),
            ("2.", "Player02", "1400"),
            ("3.", "Player03", "1350"),
            ("4.", "Player04", "1280"),
            ("5.", "Player05", "1200")
        ]

        for rank, name, elo in ranking:

            rank_label = ctk.CTkLabel(
                self.ranking_frame,
                text=f"{rank}  {name}     {elo} Elo",
                font=("Arial", 14)
            )

            rank_label.pack(
                anchor="w",
                padx=30,
                pady=8
            )

        # ==============================
        # NÚT TÌM PHÒNG
        # ==============================
        self.find_room_button = ctk.CTkButton(
            self,
            text="TÌM PHÒNG",
            width=220,
            height=45,
            font=("Arial", 15, "bold"),
            command=self.find_room
        )
        self.find_room_button.pack(
            side="left",
            padx=(100, 10),
            pady=20
        )

        # ==============================
        # NÚT LỊCH SỬ
        # ==============================
        self.history_button = ctk.CTkButton(
            self,
            text="LỊCH SỬ ĐẤU",
            width=180,
            height=45,
            command=self.show_history
        )
        self.history_button.pack(
            side="left",
            padx=10,
            pady=20
        )

        # ==============================
        # NÚT ĐĂNG XUẤT
        # ==============================
        self.logout_button = ctk.CTkButton(
            self,
            text="ĐĂNG XUẤT",
            width=150,
            height=45,
            fg_color="transparent",
            border_width=2,
            command=self.logout
        )
        self.logout_button.pack(
            side="right",
            padx=(10, 100),
            pady=20
        )

    # ==================================================
    # THÁCH ĐẤU
    # ==================================================
    def send_challenge(self, player_name):

        messagebox.showinfo(
            "Thách đấu",
            f"Đã gửi lời mời thách đấu đến {player_name}!"
        )

    # ==================================================
    # TÌM PHÒNG
    # ==================================================
    def find_room(self):

        messagebox.showinfo(
            "Tìm phòng",
            "Đang tìm phòng phù hợp..."
        )

    # ==================================================
    # LỊCH SỬ ĐẤU
    # ==================================================
    def show_history(self):

        messagebox.showinfo(
            "Lịch sử đấu",
            "Chức năng lịch sử đấu sẽ được kết nối với Backend."
        )

    # ==================================================
    # ĐĂNG XUẤT
    # ==================================================
    def logout(self):

        result = messagebox.askyesno(
            "Đăng xuất",
            "Bạn có chắc muốn đăng xuất?"
        )

        if result:
            self.destroy()


# ======================================================
# CHẠY TRỰC TIẾP FILE
# ======================================================

if __name__ == "__main__":

    app = LobbyWindow("Nga")

    app.mainloop()
