import threading
import time
from enum import Enum

class RoomState(Enum):
    WAITING = "WAITING"
    PLAYING = "PLAYING"
    FINISHED = "FINISHED"


class TurnTimer:
    def __init__(self, timeout_seconds, on_timeout_callback):
        self.timeout_seconds = timeout_seconds
        self.on_timeout_callback = on_timeout_callback
        self.timer_thread = None
        self.stop_event = threading.Event()

    def start(self):
        """Hủy Timer cũ (nếu có) và khởi tạo Timer mới"""
        self.stop()
        self.stop_event.clear()
        self.timer_thread = threading.Thread(target=self._run)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def stop(self):
        """Ngắt luồng Timer lập tức khi có nước đi hợp lệ"""
        if self.timer_thread and self.timer_thread.is_alive():
            self.stop_event.set()

    def _run(self):
        is_stopped = self.stop_event.wait(timeout=self.timeout_seconds)
        if not is_stopped:
            self.on_timeout_callback()


class CaroBoard:
    def __init__(self, size=15):
        self.size = size
        self.board = [["" for _ in range(size)] for _ in range(size)]

    def is_valid_move(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == ""

    def check_win(self, row, col, symbol):
        """
        Duyệt tối ưu: Chỉ kiểm tra 4 hướng xung quanh nước vừa đánh (row, col)
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == symbol:
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == symbol:
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True
        return False


class Room:
    def __init__(self, room_id, size=15, turn_timeout=30):
        self.room_id = room_id
        self.state = RoomState.WAITING
        self.players = {} 
        self.current_turn = None
        self.board = CaroBoard(size)
        self.winner = None
        self.turn_timeout = turn_timeout
        self.timer = TurnTimer(turn_timeout, self._handle_timeout)

    def add_player(self, player_id):
        if len(self.players) >= 2:
            return False, "Phòng đã đầy!"

        symbol = "X" if len(self.players) == 0 else "O"
        self.players[player_id] = symbol

        if len(self.players) == 2:
            self.state = RoomState.PLAYING
            self.current_turn = player_id  # Người chơi X đi trước
            self.timer.start()

        return True, f"Đã vào phòng với quân {symbol}"

    def make_move(self, player_id, row, col):
        if self.state != RoomState.PLAYING:
            return False, "Trận đấu chưa sẵn sàng hoặc đã kết thúc"

        if player_id != self.current_turn:
            return False, "Chưa đến lượt bạn!"

        symbol = self.players[player_id]
        if not self.board.is_valid_move(row, col):
            return False, "Ô đã có quân hoặc nằm ngoài bàn cờ"

        self.board.board[row][col] = symbol

        if self.board.check_win(row, col, symbol):
            self.state = RoomState.FINISHED
            self.winner = player_id
            self.timer.stop()
            return True, "WIN"

        self._switch_turn()
        self.timer.start()
        return True, "SUCCESS"

    def _switch_turn(self):
        for pid in self.players:
            if pid != self.current_turn:
                self.current_turn = pid
                break

    def _handle_timeout(self):
        """Xử lý khi 1 người chơi quá 30s không đánh (xử thua hoặc chuyển lượt)"""
        print(f"\n[EVENT BAN CỜ] Player {self.current_turn} hết 30s!")
        self._switch_turn()
        self.timer.start()

    def get_snapshot(self):
        """Ghép trạng thái bàn cờ để chuyển qua Dev 1 gửi tới Khán giả/Client"""
        return {
            "room_id": self.room_id,
            "state": self.state.value,
            "current_turn": self.current_turn,
            "winner": self.winner,
            "board": self.board.board  
        }
