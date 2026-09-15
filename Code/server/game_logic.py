# server/game_logic.py
from common.constants import BOARD_ROWS, BOARD_COLS, EMPTY, PLAYER_X, PLAYER_O, WIN_CONDITION

class CaroGame:
    def __init__(self):
        # Tạo bàn cờ 15x15 chứa toàn số 0 (EMPTY)
        self.board = [[EMPTY for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.current_turn = PLAYER_X
        self.winner = None
        self.is_draw = False

    def is_valid_move(self, row, col):
        """Kiểm tra xem nước đi có hợp lệ không (nằm trong bàn cờ và ô chưa có ai đánh)"""
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return self.board[row][col] == EMPTY
        return False

    def make_move(self, row, col, player):
        """Thực hiện một nước đi. Trả về True nếu thành công, False nếu lỗi."""
        # 1. Kiểm tra tính hợp lệ
        if self.winner or self.is_draw:
            return False, "Trận đấu đã kết thúc."
        if player != self.current_turn:
            return False, "Chưa đến lượt của bạn."
        if not self.is_valid_move(row, col):
            return False, "Nước đi không hợp lệ."

        # 2. Ghi nhận nước đi
        self.board[row][col] = player

        # 3. Kiểm tra Thắng / Thua / Hòa
        if self._check_win(row, col, player):
            self.winner = player
        elif self._check_draw():
            self.is_draw = True
        else:
            # Chuyển lượt
            self.current_turn = PLAYER_O if player == PLAYER_X else PLAYER_X

        return True, "Thành công"

    def _check_draw(self):
        """Hòa khi không còn ô trống nào trên bàn cờ"""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] == EMPTY:
                    return False
        return True

    def _check_win(self, row, col, player):
        """Thuật toán tỏa ra 4 hướng từ điểm vừa đánh để đếm số quân cờ liên tiếp"""
        # 4 hướng: Ngang, Dọc, Chéo chính (\), Chéo phụ (/)
        directions = [
            (0, 1),   # Ngang (Cột thay đổi)
            (1, 0),   # Dọc (Hàng thay đổi)
            (1, 1),   # Chéo chính (Từ trên-trái xuống dưới-phải)
            (1, -1)   # Chéo phụ (Từ trên-phải xuống dưới-trái)
        ]

        for dr, dc in directions:
            count = 1  # Tính cả quân cờ vừa đánh xuống

            # Đếm về 1 phía (chiều dương)
            r, c = row + dr, col + dc
            while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc

            # Đếm về phía ngược lại (chiều âm)
            r, c = row - dr, col - dc
            while 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc

            # Nếu đủ 5 quân liên tiếp trở lên -> Thắng
            if count >= WIN_CONDITION:
                return True

        return False