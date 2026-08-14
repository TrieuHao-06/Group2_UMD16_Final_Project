import customtkinter as ctk
from tkinter import messagebox


class CaroBoardUI(ctk.CTkFrame):
    def __init__(self, master, board_size=15):
        super().__init__(master)

        self.board_size = board_size
        self.buttons = []

        self.title_label = ctk.CTkLabel(
            self,
            text="CARO ONLINE",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=10)

        self.turn_label = ctk.CTkLabel(
            self,
            text="Lượt của: X",
            font=("Arial", 16)
        )
        self.turn_label.pack(pady=5)

        self.board_frame = ctk.CTkFrame(self)
        self.board_frame.pack(padx=10, pady=10)

        self.create_board()

    def create_board(self):
        for row in range(self.board_size):
            button_row = []

            for col in range(self.board_size):
                button = ctk.CTkButton(
                    self.board_frame,
                    text="",
                    width=35,
                    height=35,
                    command=lambda r=row, c=col: self.make_move(r, c)
                )

                button.grid(
                    row=row,
                    column=col,
                    padx=1,
                    pady=1
                )

                button_row.append(button)

            self.buttons.append(button_row)

    def make_move(self, row, col):
        button = self.buttons[row][col]

        if button.cget("text") != "":
            return

        button.configure(text="X")

        self.turn_label.configure(
            text="Lượt của: O"
        )


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Caro Online - Bàn cờ")
    app.geometry("700x700")

    board = CaroBoardUI(app)
    board.pack(expand=True, fill="both")

    app.mainloop()
