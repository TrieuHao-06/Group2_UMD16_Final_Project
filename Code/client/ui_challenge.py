import customtkinter as ctk
from tkinter import messagebox

class ChallengeDialog(ctk.CTkToplevel):
    def __init__(self, master, challenger_name: str, challenger_elo: int, on_accept_callback, on_decline_callback):
        super().__init__(master)
        
        self.title("Lời mời thách đấu")
        self.geometry("380x240")
        self.resizable(False, False)
        
        self.attributes("-topmost", True)
        self.configure(fg_color="#0F0F0F")

        self.challenger_name = challenger_name
        self.challenger_elo = challenger_elo
        self.on_accept = on_accept_callback
        self.on_decline = on_decline_callback

        self.init_ui()

    def init_ui(self):
        self.card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1E1E1E")
        self.card.pack(fill="both", expand=True, padx=15, pady=15)

        self.lbl_title = ctk.CTkLabel(
            self.card, 
            text="⚔️ LỜI MỜI THÁCH ĐẤU", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFD700" # Vàng kim
        )
        self.lbl_title.pack(pady=(15, 5))

        self.lbl_info = ctk.CTkLabel(
            self.card, 
            text=f"Người chơi {self.challenger_name}\n({self.challenger_elo} Elo)\nmuốn quyết đấu Caro với bạn!", 
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        self.lbl_info.pack(pady=10)

        self.btn_box = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_box.pack(pady=(10, 15))

        self.btn_decline = ctk.CTkButton(
            self.btn_box, 
            text="Từ chối", 
            width=110, 
            height=36,
            corner_radius=8,
            fg_color="#D9534F", 
            hover_color="#C9302C",
            command=self.handle_decline
        )
        self.btn_decline.pack(side="left", padx=10)

        self.btn_accept = ctk.CTkButton(
            self.btn_box, 
            text="Chấp nhận", 
            width=110, 
            height=36,
            corner_radius=8,
            fg_color="#28A745", 
            hover_color="#218838",
            command=self.handle_accept
        )
        self.btn_accept.pack(side="right", padx=10)

    def handle_accept(self):
        self.destroy()
        if self.on_accept:
            self.on_accept()

    def handle_decline(self):
        self.destroy()
        if self.on_decline:
            self.on_decline()


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Caro Master - Test Pop-up")
    app.geometry("500x350")
    app.configure(fg_color="#0F0F0F")

    def on_accept():
        messagebox.showinfo("Kết quả", "Bạn đã chấp nhận thách đấu! Chuyển tới bàn cờ...")

    def on_decline():
        messagebox.showinfo("Kết quả", "Bạn đã từ chối lời mời.")

    def show_popup():
        dialog = ChallengeDialog(
            app, 
            challenger_name="CaoThuCaro", 
            challenger_elo=1550, 
            on_accept_callback=on_accept, 
            on_decline_callback=on_decline
        )

    btn_test = ctk.CTkButton(app, text="Giả lập nhận lời mời thách đấu", command=show_popup)
    btn_test.pack(expand=True)

    app.mainloop()