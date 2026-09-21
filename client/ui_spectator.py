import os
import sys
import time
from queue import Empty, Queue

import pygame


BOARD_SIZE = 15
WIN_CONDITION = 5
TURN_TIME_LIMIT = 30

EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2

CELL_SIZE = 40
BOARD_OFFSET_X = 35
BOARD_OFFSET_Y = 95
BOARD_WIDTH = CELL_SIZE * (BOARD_SIZE - 1)
BOARD_HEIGHT = CELL_SIZE * (BOARD_SIZE - 1)

WINDOW_WIDTH = 980
WINDOW_HEIGHT = 720

PANEL_X = 650
PANEL_WIDTH = 300

COLOR_BG = (242, 235, 220)
COLOR_BOARD = (245, 235, 205)
COLOR_GRID = (110, 80, 55)
COLOR_X = (215, 55, 55)
COLOR_O = (35, 95, 210)
COLOR_TEXT = (35, 35, 35)
COLOR_MUTED = (105, 105, 105)
COLOR_PANEL = (250, 250, 250)
COLOR_ACCENT = (55, 125, 205)
COLOR_LAST = (255, 195, 0)
COLOR_INPUT = (238, 242, 248)


class SpectatorUI:
    """Giao diện khán giả. Không xử lý click đặt quân trên bàn cờ."""

    def __init__(
        self,
        network=None,
        match_id=None,
        player_x_name="Người chơi X",
        player_o_name="Người chơi O",
        demo=False,
    ):
        self.network = network
        self.match_id = match_id
        self.player_x_name = player_x_name
        self.player_o_name = player_o_name

        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_turn = PLAYER_X
        self.winner = None
        self.is_draw = False
        self.reason = "normal"
        self.last_move = None
        self.turn_start_time = time.time()
        self.is_running = True

        self.events = Queue()
        self.chat_messages = [("Hệ thống", "Bạn đang xem trận đấu.")]
        self.chat_input = ""
        self.chat_active = False

        self.demo = demo or network is None
        self.demo_moves = []
        self.demo_index = 0
        self.demo_last_time = time.time()

        if self.network is not None:
            self._register_network_callbacks()

    def _register_network_callbacks(self):
        """Tương thích với NetworkClient của nhóm nếu callback tồn tại."""
        register = getattr(self.network, "register_callback", None)
        if not callable(register):
            return

        register("move_made", self._queue_move)
        register("game_over", self._queue_game_over)
        register("chat_message", self._queue_chat)

    # Network callbacks chạy ở thread mạng, nên chỉ đưa dữ liệu vào Queue.
    def _queue_move(self, response):
        self.events.put(("move", response))

    def _queue_game_over(self, response):
        self.events.put(("game_over", response))

    def _queue_chat(self, response):
        self.events.put(("chat", response))

    def _process_events(self):
        while True:
            try:
                event_type, data = self.events.get_nowait()
            except Empty:
                return

            if event_type == "move":
                row = data.get("row")
                col = data.get("col")
                symbol = data.get("symbol")
                if (
                    isinstance(row, int)
                    and isinstance(col, int)
                    and 0 <= row < BOARD_SIZE
                    and 0 <= col < BOARD_SIZE
                    and symbol in (PLAYER_X, PLAYER_O)
                ):
                    self.board[row][col] = symbol
                    self.last_move = (row, col)
                    self.current_turn = data.get(
                        "next_turn",
                        PLAYER_O if symbol == PLAYER_X else PLAYER_X,
                    )
                    self.turn_start_time = time.time()

            elif event_type == "game_over":
                self.winner = data.get("winner_symbol")
                self.is_draw = bool(data.get("is_draw", False))
                self.reason = data.get("reason", "normal")

            elif event_type == "chat":
                username = data.get("username", "Người chơi")
                message = data.get("message", "")
                if message:
                    self.add_chat_message(username, message)

    def update_board(self, board_data):
        """Cho phép Client/Server gửi snapshot 15x15 trực tiếp cho spectator."""
        if not isinstance(board_data, list) or len(board_data) != BOARD_SIZE:
            return False

        new_board = []
        for row in board_data:
            if not isinstance(row, list) or len(row) != BOARD_SIZE:
                return False
            new_board.append([
                PLAYER_X if cell in (PLAYER_X, "X") else
                PLAYER_O if cell in (PLAYER_O, "O") else
                EMPTY
                for cell in row
            ])

        self.board = new_board
        return True

    def update_status(self, current_turn=None, winner=None, is_draw=False, reason="normal"):
        if current_turn in (PLAYER_X, PLAYER_O):
            self.current_turn = current_turn
            self.turn_start_time = time.time()
        self.winner = winner
        self.is_draw = is_draw
        self.reason = reason

    def add_chat_message(self, username, message):
        if not message:
            return
        self.chat_messages.append((str(username), str(message)))
        self.chat_messages = self.chat_messages[-8:]

    def _send_chat(self):
        message = self.chat_input.strip()
        if not message:
            return

        self.add_chat_message("Bạn", message)
        self.chat_input = ""

        if self.network is not None and self.match_id:
            send = getattr(self.network, "send", None)
            if callable(send):
                send({
                    "action": "chat_message",
                    "match_id": self.match_id,
                    "message": message,
                })

    def _setup_demo(self):
        # Demo X tạo 5 quân ngang để chứng minh UI nhận dữ liệu trận.
        self.demo_moves = [
            (7, 5, PLAYER_X),
            (6, 5, PLAYER_O),
            (7, 6, PLAYER_X),
            (6, 6, PLAYER_O),
            (7, 7, PLAYER_X),
            (6, 7, PLAYER_O),
            (7, 8, PLAYER_X),
            (6, 8, PLAYER_O),
            (7, 9, PLAYER_X),
        ]
        self.demo_index = 0
        self.demo_last_time = time.time()

    def _update_demo(self):
        if self.winner or self.is_draw:
            return

        if self.demo_index < len(self.demo_moves):
            if time.time() - self.demo_last_time >= 0.65:
                row, col, symbol = self.demo_moves[self.demo_index]
                self.board[row][col] = symbol
                self.last_move = (row, col)
                self.current_turn = PLAYER_O if symbol == PLAYER_X else PLAYER_X
                self.turn_start_time = time.time()
                self.demo_index += 1
                self.demo_last_time = time.time()
        elif time.time() - self.demo_last_time >= 1:
            self.winner = PLAYER_X
            self.reason = "normal"

    def run(self):
        pygame.init()
        pygame.font.init()

        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Caro Online - Khán giả")
        clock = pygame.time.Clock()

        font_title = pygame.font.SysFont("Segoe UI", 25, bold=True)
        font_main = pygame.font.SysFont("Segoe UI", 18, bold=True)
        font_small = pygame.font.SysFont("Segoe UI", 15)
        font_tiny = pygame.font.SysFont("Segoe UI", 13)

        if self.demo:
            self._setup_demo()

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False
                    elif event.key == pygame.K_RETURN and self.chat_active:
                        self._send_chat()
                    elif event.key == pygame.K_BACKSPACE and self.chat_active:
                        self.chat_input = self.chat_input[:-1]
                    elif self.chat_active and event.unicode and len(self.chat_input) < 45:
                        self.chat_input += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Không xử lý click trên bàn cờ.
                    # Chỉ click ô chat mới có tác dụng.
                    input_rect = pygame.Rect(
                        PANEL_X + 15, WINDOW_HEIGHT - 65, PANEL_WIDTH - 30, 38
                    )
                    self.chat_active = input_rect.collidepoint(event.pos)

            self._process_events()
            if self.demo:
                self._update_demo()

            remaining = max(
                0,
                TURN_TIME_LIMIT - int(time.time() - self.turn_start_time)
            )

            self._draw(screen, font_title, font_main, font_small, font_tiny, remaining)
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

    def _draw(self, screen, font_title, font_main, font_small, font_tiny, remaining):
        screen.fill(COLOR_BG)

        title = font_title.render("CARO ONLINE — KHÁN GIẢ", True, COLOR_TEXT)
        screen.blit(title, (BOARD_OFFSET_X, 25))

        subtitle = font_tiny.render(
            "CHẾ ĐỘ CHỈ XEM • Không thể đặt quân",
            True,
            COLOR_MUTED,
        )
        screen.blit(subtitle, (BOARD_OFFSET_X, 58))

        self._draw_board(screen)
        self._draw_panel(screen, font_main, font_small, font_tiny, remaining)

        if self.winner or self.is_draw:
            self._draw_result(screen, font_main, font_small)

    def _draw_board(self, screen):
        board_rect = pygame.Rect(
            BOARD_OFFSET_X - 12,
            BOARD_OFFSET_Y - 12,
            BOARD_WIDTH + 24,
            BOARD_HEIGHT + 24,
        )
        pygame.draw.rect(screen, COLOR_BOARD, board_rect, border_radius=8)

        for i in range(BOARD_SIZE):
            y = BOARD_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(
                screen, COLOR_GRID,
                (BOARD_OFFSET_X, y),
                (BOARD_OFFSET_X + BOARD_WIDTH, y), 2
            )

            x = BOARD_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(
                screen, COLOR_GRID,
                (x, BOARD_OFFSET_Y),
                (x, BOARD_OFFSET_Y + BOARD_HEIGHT), 2
            )

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cx = BOARD_OFFSET_X + col * CELL_SIZE
                cy = BOARD_OFFSET_Y + row * CELL_SIZE

                if self.last_move == (row, col):
                    pygame.draw.circle(
                        screen, COLOR_LAST, (cx, cy), CELL_SIZE // 2 - 2, 3
                    )

                if self.board[row][col] == PLAYER_X:
                    d = 11
                    pygame.draw.line(screen, COLOR_X, (cx-d, cy-d), (cx+d, cy+d), 4)
                    pygame.draw.line(screen, COLOR_X, (cx+d, cy-d), (cx-d, cy+d), 4)

                elif self.board[row][col] == PLAYER_O:
                    pygame.draw.circle(screen, COLOR_O, (cx, cy), 13, 4)

    def _draw_panel(self, screen, font_main, font_small, font_tiny, remaining):
        panel = pygame.Rect(PANEL_X, 20, PANEL_WIDTH, WINDOW_HEIGHT - 40)
        pygame.draw.rect(screen, COLOR_PANEL, panel, border_radius=12)

        screen.blit(
            font_main.render("THÔNG TIN TRẬN", True, COLOR_TEXT),
            (PANEL_X + 15, 38)
        )

        pygame.draw.circle(screen, COLOR_X, (PANEL_X + 25, 88), 7)
        screen.blit(
            font_small.render("X  " + self.player_x_name, True, COLOR_TEXT),
            (PANEL_X + 40, 78)
        )

        pygame.draw.circle(screen, COLOR_O, (PANEL_X + 25, 120), 7)
        screen.blit(
            font_small.render("O  " + self.player_o_name, True, COLOR_TEXT),
            (PANEL_X + 40, 110)
        )

        if self.winner or self.is_draw:
            status = "Trận đấu đã kết thúc"
        else:
            current = (
                self.player_x_name
                if self.current_turn == PLAYER_X
                else self.player_o_name
            )
            status = "Lượt: " + current

        screen.blit(
            font_small.render(status, True, COLOR_ACCENT),
            (PANEL_X + 15, 155)
        )
        screen.blit(
            font_small.render(f"Thời gian lượt: {remaining}s", True, COLOR_TEXT),
            (PANEL_X + 15, 185)
        )

        screen.blit(
            font_main.render("CHAT", True, COLOR_TEXT),
            (PANEL_X + 15, 225)
        )

        chat_box = pygame.Rect(PANEL_X + 15, 255, PANEL_WIDTH - 30, 245)
        pygame.draw.rect(screen, (245, 247, 250), chat_box, border_radius=8)

        y = 267
        for username, message in self.chat_messages:
            text = f"{username}: {message}"
            if len(text) > 36:
                text = text[:33] + "..."
            screen.blit(
                font_tiny.render(text, True, COLOR_TEXT),
                (PANEL_X + 25, y)
            )
            y += 27
            if y > 475:
                break

        input_rect = pygame.Rect(
            PANEL_X + 15, WINDOW_HEIGHT - 65, PANEL_WIDTH - 30, 38
        )
        fill = COLOR_INPUT if self.chat_active else (225, 225, 225)
        pygame.draw.rect(screen, fill, input_rect, border_radius=7)
        pygame.draw.rect(screen, COLOR_ACCENT, input_rect, 2, border_radius=7)

        placeholder = self.chat_input or "Nhập tin nhắn... (Enter)"
        color = COLOR_TEXT if self.chat_input else COLOR_MUTED
        screen.blit(
            font_tiny.render(placeholder, True, color),
            (input_rect.x + 10, input_rect.y + 10)
        )

    def _draw_result(self, screen, font_main, font_small):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        if self.is_draw:
            result = "TRẬN ĐẤU HÒA"
        elif self.winner == PLAYER_X:
            result = f"{self.player_x_name} THẮNG"
        else:
            result = f"{self.player_o_name} THẮNG"

        reason = "Hết thời gian" if self.reason == "timeout" else "Đủ 5 quân liên tiếp"

        text = font_main.render(result, True, (255, 215, 0))
        screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, 330)))

        sub = font_small.render(reason, True, (255, 255, 255))
        screen.blit(sub, sub.get_rect(center=(WINDOW_WIDTH // 2, 370)))


if __name__ == "__main__":
    SpectatorUI(demo=True).run()
