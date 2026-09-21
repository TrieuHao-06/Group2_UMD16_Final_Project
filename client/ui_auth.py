import customtkinter as ctk
from tkinter import messagebox


class AuthWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ==============================
        # CẤU HÌNH CỬA SỔ
        # ==============================
        self.title("Caro Online - Đăng nhập")
        self.geometry("450x550")
        self.resizable(False, False)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # ==============================
        # TIÊU ĐỀ
        # ==============================
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

        # ==============================
        # USERNAME
        # ==============================
        self.username_entry = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Tên đăng nhập"
        )
        self.username_entry.pack(pady=10)

        # ==============================
        # PASSWORD
        # ==============================
        self.password_entry = ctk.CTkEntry(
            self,
            width=320,
            height=45,
            placeholder_text="Mật khẩu",
            show="*"
        )
        self.password_entry.pack(pady=10)

        # ==============================
        # NÚT ĐĂNG NHẬP
        # ==============================
        self.login_button = ctk.CTkButton(
            self,
            text="ĐĂNG NHẬP",
            width=320,
            height=45,
            command=self.login
        )
        self.login_button.pack(pady=(25, 10))

        # ==============================
        # NÚT ĐĂNG KÝ
        # ==============================
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

        # ==============================
        # THÔNG BÁO
        # ==============================
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=15)

        # ==============================
        # FOOTER
        # ==============================
        self.footer_label = ctk.CTkLabel(
            self,
            text="Game Caro Online 15x15",
            font=("Arial", 11)
        )
        self.footer_label.pack(side="bottom", pady=20)

    # ==================================================
    # XỬ LÝ ĐĂNG NHẬP
    # ==================================================
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Kiểm tra dữ liệu nhập
        if not username:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập tên đăng nhập!"
            )
            self.username_entry.focus()
            return

        if not password:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập mật khẩu!"
            )
            self.password_entry.focus()
            return

        # Hiện tại chỉ kiểm tra giao diện.
        # Sau này kết nối API của Vĩ/Hào tại đây.
        messagebox.showinfo(
            "Đăng nhập",
            f"Đăng nhập thành công!\n\nTài khoản: {username}"
        )

        self.status_label.configure(
            text=f"Xin chào {username}!"
        )

    # ==================================================
    # XỬ LÝ ĐĂNG KÝ
    # ==================================================
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập tên đăng nhập!"
            )
            self.username_entry.focus()
            return

        if not password:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập mật khẩu!"
            )
            self.password_entry.focus()
            return

        if len(password) < 6:
            messagebox.showwarning(
                "Mật khẩu không hợp lệ",
                "Mật khẩu phải có ít nhất 6 ký tự!"
            )
            self.password_entry.focus()
            return

        # Hiện tại chỉ xử lý giao diện.
        # Sau này kết nối API đăng ký của Backend.
        messagebox.showinfo(
            "Đăng ký",
            f"Tạo tài khoản thành công!\n\n"
            f"Tài khoản: {username}"
        )

    # ==================================================
    # XÓA DỮ LIỆU FORM
    # ==================================================
    def clear_form(self):
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.status_label.configure(text="")


# ======================================================
# CHẠY TRỰC TIẾP FILE
# ======================================================
if __name__ == "__main__":
    app = AuthWindow()
    app.mainloop()
