# tests/test_game_logic.py
"""
Kiểm thử thuật toán Caro 5 quân trong Code/Dev2.py.
"""
from Code.Dev2 import CaroBoard


def test_horizontal_five():
    board = CaroBoard(15)
    for col in range(5):
        board.board[3][col] = "X"

    assert board.check_win(3, 4, "X") is True


def test_vertical_five():
    board = CaroBoard(15)
    for row in range(5):
        board.board[row][4] = "O"

    assert board.check_win(4, 4, "O") is True


def test_main_diagonal_five():
    board = CaroBoard(15)
    for i in range(5):
        board.board[i][i] = "X"

    assert board.check_win(4, 4, "X") is True


def test_anti_diagonal_five():
    board = CaroBoard(15)
    for i in range(5):
        board.board[i][4 - i] = "O"

    assert board.check_win(4, 0, "O") is True


def test_four_is_not_win():
    board = CaroBoard(15)
    for col in range(4):
        board.board[5][col] = "X"

    assert board.check_win(5, 3, "X") is False


def test_six_is_win():
    board = CaroBoard(15)
    for col in range(6):
        board.board[5][col] = "X"

    assert board.check_win(5, 3, "X") is True


def test_blocked_four_is_not_win():
    board = CaroBoard(15)
    board.board[7][1] = "O"
    for col in range(2, 6):
        board.board[7][col] = "X"
    board.board[7][6] = "O"

    assert board.check_win(7, 3, "X") is False


def test_out_of_board_move():
    board = CaroBoard(15)

    assert board.is_valid_move(-1, 0) is False
    assert board.is_valid_move(0, -1) is False
    assert board.is_valid_move(15, 0) is False
    assert board.is_valid_move(0, 15) is False


def test_valid_empty_move():
    board = CaroBoard(15)

    assert board.is_valid_move(7, 7) is True
    board.board[7][7] = "X"
    assert board.is_valid_move(7, 7) is False
