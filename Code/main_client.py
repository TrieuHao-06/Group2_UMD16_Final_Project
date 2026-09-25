import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.network import NetworkClient
from client.ui_auth import AuthFrame
from client.ui_lobby import LobbyFrame
from client.ui_challenge import ChallengeDialog

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Caro Master - Client Application")
        self.geometry("450x600")
        self.configure(fg_color="#0F0F0F")

        self.network_client = NetworkClient()
        success, msg = self.network_client.connect()
        if not success:
            messagebox.showerror("Lỗi Kết Nối", msg)
            
        self.current_user = None

        self.current_frame = None

        self.show_auth_screen()

    def clear_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_auth_screen(self):
        self.clear_current_frame()
        self.geometry("450x600") 
        
        self.current_frame = AuthFrame(
            self, 
            network_client=self.network_client, 
            on_login_success_callback=self.handle_login_success
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_lobby_screen(self):
        self.clear_current_frame()
        self.geometry("850x620") 

        self.current_frame = LobbyFrame(
            self, 
            network_client=self.network_client, 
            user_data=self.current_user, 
            on_logout_callback=self.handle_logout, 
            on_start_game_callback=self.handle_start_game
        )
        self.current_frame.pack(fill="both", expand=True)

    def handle_login_success(self, user_info):
        self.current_user = user_info
        self.show_lobby_screen()

    def handle_logout(self):
        self.current_user = None
        self.show_auth_screen()

    def handle_start_game(self, room_id):
        # Điểm bàn giao cho Pygame của Sơn Hào ở Tuần 3
        messagebox.showinfo(
            "Bàn giao Pygame", 
            f"Vào phòng: {room_id}\n\nẨn cửa sổ CustomTkinter và khởi chạy bàn cờ Pygame của Sơn Hào..."
        )

    def trigger_incoming_challenge(self, challenger_name, challenger_elo):
        """Giả lập khi Socket nhận được lời mời thách đấu từ người khác"""
        def on_accept():
            self.handle_start_game(f"MATCH_{challenger_name}")

        def on_decline():
            messagebox.showinfo("Thông báo", "Đã từ chối lời mời.")

        ChallengeDialog(
            self, 
            challenger_name=challenger_name, 
            challenger_elo=challenger_elo, 
            on_accept_callback=on_accept, 
            on_decline_callback=on_decline
        )


if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()