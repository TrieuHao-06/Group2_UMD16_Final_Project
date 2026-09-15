# client/ui_board.py
import pygame
import time
from common.constants import (
    BOARD_ROWS, BOARD_COLS, EMPTY, PLAYER_X, PLAYER_O, TURN_TIME_LIMIT
)

CELL_SIZE = 40
GRID_SIZE = 15
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 80
WINDOW_WIDTH = BOARD_OFFSET_X * 2 + CELL_SIZE * (GRID_SIZE - 1)
WINDOW_HEIGHT = BOARD_OFFSET_Y + CELL_SIZE * (GRID_SIZE - 1) + 60

COLOR_BG = (245, 235, 220)
COLOR_GRID = (120, 90, 60)
COLOR_X = (220, 50, 50)
COLOR_O = (30, 100, 220)
COLOR_TEXT = (40, 40, 40)
COLOR_HIGHLIGHT = (255, 215, 0)

class CaroBoardUI:
    def __init__(self, network, match_id, my_symbol, opponent_name):
        self.network = network
        self.match_id = match_id
        self.my_symbol = my_symbol
        self.opponent_name = opponent_name

        self.board = [[EMPTY for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.current_turn = PLAYER_X
        self.winner = None
        self.is_draw = False
        self.reason = "normal"
        self.last_move = None
        self.turn_start_time = time.time()
        self.game_over_time = None
        self.is_running = True

        self.network.register_callback("move_made", self._on_move_made)
        self.network.register_callback("game_over", self._on_game_over)

    def run(self):
        pygame.init()
        pygame.font.init()

        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"Trận Đấu Caro - Bạn là: {('Quân X' if self.my_symbol == PLAYER_X else 'Quân O')}")
        clock = pygame.time.Clock()

        try:
            font_main = pygame.font.SysFont("Segoe UI", 22, bold=True)
            font_sub = pygame.font.SysFont("Segoe UI", 16)
        except Exception:
            font_main = pygame.font.Font(None, 26)
            font_sub = pygame.font.Font(None, 20)

        pygame.event.pump()
        screen.fill(COLOR_BG)
        pygame.display.flip()

        self.turn_start_time = time.time()

        try:
            while self.is_running:
                # Nếu đã có kết quả -> Tự động thoát sau 4 giây hiển thị thông báo
                if (self.winner or self.is_draw) and self.game_over_time:
                    if time.time() - self.game_over_time > 4.0:
                        self.is_running = False

                elapsed_time = int(time.time() - self.turn_start_time)
                remaining_time = max(0, TURN_TIME_LIMIT - elapsed_time)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.winner is None and not self.is_draw and self.current_turn == self.my_symbol:
                            pos = pygame.mouse.get_pos()
                            row, col = self._get_cell_from_pos(pos)
                            if row is not None and col is not None and self.board[row][col] == EMPTY:
                                self.network.send({
                                    "action": "make_move",
                                    "match_id": self.match_id,
                                    "row": row,
                                    "col": col
                                })

                screen.fill(COLOR_BG)
                self._draw_grid(screen)
                self._draw_pieces(screen)
                self._draw_header(screen, font_main, remaining_time)

                if self.winner or self.is_draw:
                    self._draw_winner_overlay(screen, font_main, font_sub)

                pygame.display.flip()
                clock.tick(30)

        finally:
            pygame.quit()

    def _on_move_made(self, response):
        row = response.get("row")
        col = response.get("col")
        symbol = response.get("symbol")
        next_turn = response.get("next_turn")

        self.board[row][col] = symbol
        self.last_move = (row, col)
        self.current_turn = next_turn
        self.turn_start_time = time.time()

    def _on_game_over(self, response):
        self.winner = response.get("winner_symbol")
        self.is_draw = response.get("is_draw", False)
        self.reason = response.get("reason", "normal")
        self.game_over_time = time.time() # Đánh dấu thời điểm kết thúc trận

    def _get_cell_from_pos(self, pos):
        x, y = pos
        col = round((x - BOARD_OFFSET_X) / CELL_SIZE)
        row = round((y - BOARD_OFFSET_Y) / CELL_SIZE)
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return row, col
        return None, None

    def _draw_header(self, screen, font, remaining_time):
        if self.winner or self.is_draw:
            turn_str = "TRẬN ĐẤU ĐÃ KẾT THÚC"
            turn_color = COLOR_TEXT
        else:
            turn_str = "Lượt của BẠN" if self.current_turn == self.my_symbol else f"Lượt của {self.opponent_name}"
            turn_color = COLOR_X if self.current_turn == PLAYER_X else COLOR_O

        txt_turn = font.render(turn_str, True, turn_color)
        screen.blit(txt_turn, (BOARD_OFFSET_X, 20))

        timer_str = f"Thời gian: {remaining_time}s"
        timer_color = (200, 30, 30) if remaining_time <= 5 else COLOR_TEXT
        txt_timer = font.render(timer_str, True, timer_color)
        screen.blit(txt_timer, (WINDOW_WIDTH - BOARD_OFFSET_X - txt_timer.get_width(), 20))

    def _draw_grid(self, screen):
        for i in range(GRID_SIZE):
            start_pos = (BOARD_OFFSET_X, BOARD_OFFSET_Y + i * CELL_SIZE)
            end_pos = (BOARD_OFFSET_X + (GRID_SIZE - 1) * CELL_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE)
            pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos, 2)

            start_pos = (BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y)
            end_pos = (BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y + (GRID_SIZE - 1) * CELL_SIZE)
            pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos, 2)

    def _draw_pieces(self, screen):
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                center_x = BOARD_OFFSET_X + c * CELL_SIZE
                center_y = BOARD_OFFSET_Y + r * CELL_SIZE

                if self.last_move == (r, c):
                    pygame.draw.circle(screen, COLOR_HIGHLIGHT, (center_x, center_y), CELL_SIZE // 2 - 2, 3)

                if self.board[r][c] == PLAYER_X:
                    delta = 12
                    pygame.draw.line(screen, COLOR_X, (center_x - delta, center_y - delta), (center_x + delta, center_y + delta), 4)
                    pygame.draw.line(screen, COLOR_X, (center_x + delta, center_y - delta), (center_x - delta, center_y + delta), 4)

                elif self.board[r][c] == PLAYER_O:
                    pygame.draw.circle(screen, COLOR_O, (center_x, center_y), 13, 4)

    def _draw_winner_overlay(self, screen, font_main, font_sub):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        if self.is_draw:
            win_txt = "TRẬN ĐẤU HÒA!"
        elif self.winner == self.my_symbol:
            win_txt = "BẠN ĐÃ THẮNG! 🎉"
        else:
            win_txt = "BẠN ĐÃ THUA! 😿"

        txt_surface = font_main.render(win_txt, True, (255, 215, 0) if self.winner == self.my_symbol else (255, 255, 255))
        rect = txt_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        screen.blit(txt_surface, rect)

        # Thông báo chi tiết lý do thắng thua
        if self.reason == "timeout":
            sub_str = "(Đối thủ hết thời gian lượt đi)" if self.winner == self.my_symbol else "(Bạn đã hết thời gian lượt đi)"
        else:
            sub_str = "Đang quay về sảnh chờ trong giây lát..."

        txt_sub = font_sub.render(sub_str, True, (200, 200, 200))
        rect_sub = txt_sub.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))
        screen.blit(txt_sub, rect_sub)