import customtkinter as ctk
from tkinter import messagebox


class AuthWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Caro Online - Đăng nhập")
        self.geometry("450x550")
        self.resizable(False, False)

        # =========================
        # CẤU HÌNH GIAO DIỆN
        # =========================
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # =========================
        # TIÊU ĐỀ
        # =========================
        self.title_label = ctk.CTkLabel(
            self,
            text="CARO ONLINE",
            font=("Arial", 30, "bold")
        )
        self.title_label.pack(pady=(50, 10))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Đăng nhập tài khoản",
            font=("Arial", 16)
        )
        self.subtitle_label.pack(pady=(0, 30))

        # =========================
        # USERNAME
        # =========================
        self.username_entry = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Tên đăng nhập"
        )
        self.username_entry.pack(pady=10)

        # =========================
        # PASSWORD
        # =========================
        self.password_entry = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Mật khẩu",
            show="*"
        )
        self.password_entry.pack(pady=10)

        # =========================
        # NÚT ĐĂNG NHẬP
        # =========================
        self.login_button = ctk.CTkButton(
            self,
            text="ĐĂNG NHẬP",
            width=320,
            height=45,
            command=self.login
        )
        self.login_button.pack(pady=(25, 10))

        # =========================
        # NÚT ĐĂNG KÝ
        # =========================
        self.register_button = ctk.CTkButton(
            self,
            text="ĐĂNG KÝ TÀI KHOẢN",
            width=320,
            height=45,
            fg_color="transparent",
            border_width=2,
            command=self.register
        )
        self.register_button.pack(pady=10)

        # =========================
        # TRẠNG THÁI
        # =========================
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            text_color="gray"
        )
        self.status_label.pack(pady=20)

    # =========================
    # XỬ LÝ ĐĂNG NHẬP
    # =========================
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!"
            )
            return

        self.status_label.configure(
            text="Đang gửi yêu cầu đăng nhập..."
        )

        # TODO:
        # Kết nối API của Hào/Hải tại đây
        #
        # Ví dụ sau này:
        # response = api_client.login(username, password)

        messagebox.showinfo(
            "Đăng nhập",
            f"Đã nhận thông tin đăng nhập của: {username}"
        )

        self.status_label.configure(
            text="Đăng nhập thành công!"
        )

    # =========================
    # XỬ LÝ ĐĂNG KÝ
    # =========================
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning(
                "Thông báo",
                "Vui lòng nhập tên đăng nhập và mật khẩu!"
            )
            return

        # TODO:
        # Kết nối API đăng ký của Backend

        messagebox.showinfo(
            "Đăng ký",
            "Giao diện đăng ký đã sẵn sàng.\n"
            "Sẽ kết nối Backend ở bước tiếp theo."
        )


# =========================
# CHẠY CHƯƠNG TRÌNH
# =========================
if __name__ == "__main__":
    app = AuthWindow()
    app.mainloop()
