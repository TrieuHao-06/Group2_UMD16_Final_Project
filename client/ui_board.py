import customtkinter as ctk


class CaroBoardUI(ctk.CTkFrame):
    def __init__(self, master, board_size=15):
        super().__init__(master)

        self.board_size = board_size

        # Lưu trạng thái các ô trên giao diện
        self.board = [
            ["" for _ in range(board_size)]
            for _ in range(board_size)
        ]

        # Lưu các button
        self.buttons = []

        # Quân hiện tại
        self.current_symbol = "X"

        # =========================
        # TIÊU ĐỀ
        # =========================

        self.title_label = ctk.CTkLabel(
            self,
            text="CARO ONLINE",
            font=("Arial", 24, "bold")
        )

        self.title_label.pack(pady=10)

        # =========================
        # HIỂN THỊ LƯỢT
        # =========================

        self.turn_label = ctk.CTkLabel(
            self,
            text="Lượt của: X",
            font=("Arial", 16)
        )

        self.turn_label.pack(pady=5)

        # =========================
        # BÀN CỜ
        # =========================

        self.board_frame = ctk.CTkFrame(self)

        self.board_frame.pack(
            padx=10,
            pady=10
        )

        self.create_board()

    # =========================
    # TẠO BÀN CỜ
    # =========================

    def create_board(self):

        for row in range(self.board_size):

            button_row = []

            for col in range(self.board_size):

                button = ctk.CTkButton(
                    self.board_frame,
                    text="",
                    width=35,
                    height=35,
                    command=lambda r=row, c=col:
                    self.make_move(r, c)
                )

                button.grid(
                    row=row,
                    column=col,
                    padx=1,
                    pady=1
                )

                button_row.append(button)

            self.buttons.append(button_row)

    # =========================
    # ĐÁNH CỜ
    # =========================

    def make_move(self, row, col):

        # Nếu ô đã có quân thì không cho đánh
        if self.board[row][col] != "":
            return

        # Đặt quân vào board
        self.board[row][col] = self.current_symbol

        # Hiển thị quân lên giao diện
        self.buttons[row][col].configure(
            text=self.current_symbol
        )

        # Đổi lượt
        if self.current_symbol == "X":
            self.current_symbol = "O"
        else:
            self.current_symbol = "X"

        # Cập nhật thông báo lượt
        self.turn_label.configure(
            text=f"Lượt của: {self.current_symbol}"
        )

    # =========================
    # LẤY TRẠNG THÁI BÀN CỜ
    # =========================

    def get_board(self):
        return self.board

    # =========================
    # CẬP NHẬT BÀN CỜ
    # DÙNG KHI NHẬN DỮ LIỆU TỪ SERVER
    # =========================

    def update_board(self, board_data):

        self.board = board_data

        for row in range(self.board_size):

            for col in range(self.board_size):

                self.buttons[row][col].configure(
                    text=self.board[row][col]
                )

    # =========================
    # RESET BÀN CỜ
    # =========================

    def reset_board(self):

        self.board = [
            ["" for _ in range(self.board_size)]
            for _ in range(self.board_size)
        ]

        self.current_symbol = "X"

        for row in range(self.board_size):

            for col in range(self.board_size):

                self.buttons[row][col].configure(
                    text=""
                )

        self.turn_label.configure(
            text="Lượt của: X"
        )


# ==========================================
# CHẠY TEST GIAO DIỆN
# ==========================================

if __name__ == "__main__":

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()

    app.title("Caro Online - Bàn cờ")

    app.geometry("700x700")

    board = CaroBoardUI(app)

    board.pack(
        expand=True,
        fill="both"
    )

    app.mainloop()
