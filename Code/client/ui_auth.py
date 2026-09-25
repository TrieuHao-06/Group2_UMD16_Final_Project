import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from client.network import NetworkClient
except ImportError:
    from network import NetworkClient

# Thiết lập Giao diện Toàn cầu
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class AuthFrame(ctk.CTkFrame):
    def __init__(self, master, network_client: NetworkClient, on_login_success_callback):
        # Đặt fg_color="transparent" để Frame chính tệp với màu nền của App
        super().__init__(master, fg_color="transparent") 
        self.network_client = network_client
        self.on_login_success = on_login_success_callback
        
        self.network_client.register_callback("login_response", self.on_login_response)
        self.network_client.register_callback("register_response", self.on_register_response)

        self.init_ui()

    def init_ui(self):
        # Tiêu đề Game to, rõ, font hiện đại
        self.title_label = ctk.CTkLabel(
            self, 
            text="CARO MASTER", 
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color="#3B8ED0" # Màu xanh dương sáng
        )
        self.title_label.pack(pady=(40, 5))

        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Đăng nhập để bắt đầu thách đấu", 
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 20))

        # Card Frame: Khối hộp chứa form (Bo góc 15)
        self.card_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E1E")
        self.card_frame.pack(padx=20, pady=10, ipadx=10, ipady=10)

        # Tabview (Sửa lại cho tiệp màu với Card Frame)
        self.tabview = ctk.CTkTabview(
            self.card_frame, 
            width=320, 
            height=320, 
            corner_radius=10,
            fg_color="#1E1E1E",
            segmented_button_fg_color="#2B2B2B",
            segmented_button_selected_color="#3B8ED0"
        )
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        self.tab_login = self.tabview.add("Đăng Nhập")
        self.tab_register = self.tabview.add("Đăng Ký")

        self.setup_login_tab()
        self.setup_register_tab()

    # ---------------------------------------------------------
    # TAB ĐĂNG NHẬP (Làm mượt Input & Button)
    # ---------------------------------------------------------
    def setup_login_tab(self):
        self.login_user_entry = ctk.CTkEntry(
            self.tab_login, 
            placeholder_text="Tên đăng nhập", 
            width=280, 
            height=40,
            corner_radius=8,
            border_width=1
        )
        self.login_user_entry.pack(pady=(25, 10))

        self.login_pass_entry = ctk.CTkEntry(
            self.tab_login, 
            placeholder_text="Mật khẩu", 
            show="•", 
            width=280, 
            height=40,
            corner_radius=8,
            border_width=1
        )
        self.login_pass_entry.pack(pady=10)

        self.login_msg_label = ctk.CTkLabel(
            self.tab_login, text="", text_color="#FF4C4C", font=ctk.CTkFont(size=12)
        )
        self.login_msg_label.pack(pady=2)

        self.btn_login = ctk.CTkButton(
            self.tab_login, 
            text="ĐĂNG NHẬP", 
            width=280, 
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.handle_login
        )
        self.btn_login.pack(pady=(15, 10))

    def handle_login(self):
        username = self.login_user_entry.get().strip()
        password = self.login_pass_entry.get().strip()

        # Hiệu ứng loading nhẹ
        self.btn_login.configure(text="ĐANG XỬ LÝ...", state="disabled")
        self.update()

        self.network_client.send({
            "action": "login",
            "username": username,
            "password": password
        })

    def on_login_response(self, response):
        status = response.get("status")
        message = response.get("message")
        
        if status == "success":
            self.login_msg_label.configure(text=message, text_color="#28A745") # Xanh lá
            user_info = response.get("data")
            self.after(500, lambda: self.on_login_success(user_info))
        else:
            self.login_msg_label.configure(text=message, text_color="#FF4C4C") # Đỏ
            self.btn_login.configure(text="ĐĂNG NHẬP", state="normal")

    # ---------------------------------------------------------
    # TAB ĐĂNG KÝ
    # ---------------------------------------------------------
    def setup_register_tab(self):
        self.reg_user_entry = ctk.CTkEntry(
            self.tab_register, placeholder_text="Tên đăng nhập", width=280, height=35, border_width=1
        )
        self.reg_user_entry.pack(pady=(15, 5))

        self.reg_email_entry = ctk.CTkEntry(
            self.tab_register, placeholder_text="Email", width=280, height=35, border_width=1
        )
        self.reg_email_entry.pack(pady=5)

        self.reg_pass_entry = ctk.CTkEntry(
            self.tab_register, placeholder_text="Mật khẩu", show="•", width=280, height=35, border_width=1
        )
        self.reg_pass_entry.pack(pady=5)

        self.reg_confirm_pass_entry = ctk.CTkEntry(
            self.tab_register, placeholder_text="Xác nhận mật khẩu", show="•", width=280, height=35, border_width=1
        )
        self.reg_confirm_pass_entry.pack(pady=5)

        self.reg_msg_label = ctk.CTkLabel(
            self.tab_register, text="", text_color="#FF4C4C", font=ctk.CTkFont(size=12)
        )
        self.reg_msg_label.pack(pady=2)

        self.btn_register = ctk.CTkButton(
            self.tab_register, 
            text="TẠO TÀI KHOẢN", 
            width=280, 
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.handle_register
        )
        self.btn_register.pack(pady=(10, 5))

    def handle_register(self):
        username = self.reg_user_entry.get().strip()
        email = self.reg_email_entry.get().strip()
        password = self.reg_pass_entry.get().strip()
        confirm_pass = self.reg_confirm_pass_entry.get().strip()

        print(f"[UI_AUTH DEBUG] Chuẩn bị gửi đăng ký: username='{username}', email='{email}', password='{password}'")

        if password != confirm_pass:
            self.reg_msg_label.configure(text="Mật khẩu xác nhận không khớp!", text_color="#FF4C4C")
            return

        self.btn_register.configure(text="ĐANG TẠO...", state="disabled")
        self.update()

        self.network_client.send({
            "action": "register",
            "username": username,
            "password": password,
            "email": email
        })

    def on_register_response(self, response):
        status = response.get("status")
        message = response.get("message")

        if status == "success":
            self.reg_msg_label.configure(text=message, text_color="#28A745")
            messagebox.showinfo("Thành công", "Tạo tài khoản thành công! Vui lòng đăng nhập.")
            self.tabview.set("Đăng Nhập")
        else:
            self.reg_msg_label.configure(text=message, text_color="#FF4C4C")
        
        self.btn_register.configure(text="TẠO TÀI KHOẢN", state="normal")


# =========================================================
# CHẠY TEST ĐỘC LẬP
# =========================================================
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Caro Master - Đăng Nhập")
    # Tăng kích thước cửa sổ để UI có không gian thở
    app.geometry("450x600") 
    app.configure(fg_color="#0F0F0F") # Đen nhám hiện đại

    net_client = NetworkClient()
    net_client.connect()

    def on_success(user_data):
        messagebox.showinfo("Welcome", f"Đăng nhập thành công!\nXin chào: {user_data['username']}")

    auth_ui = AuthFrame(app, network_client=net_client, on_login_success_callback=on_success)
    auth_ui.pack(fill="both", expand=True)

    app.mainloop()