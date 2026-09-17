# tests/test_game_logic.py
import pytest
from server.game_logic import CaroGame
from common.constants import PLAYER_X, PLAYER_O

def test_horizontal_win():
    game = CaroGame()
    # X đánh hàng ngang từ cột 0 đến 4 ở hàng 0
    for i in range(4):
        game.make_move(0, i, PLAYER_X)  # X đánh
        game.make_move(1, i, PLAYER_O)  # O đánh phòng thủ hàng dưới
    
    # Nước thứ 5 quyết định của X
    success, msg = game.make_move(0, 4, PLAYER_X)
    
    assert success is True
    assert game.winner == PLAYER_X

def test_diagonal_win():
    game = CaroGame()
    # X đánh chéo chính từ (0,0) đến (4,4)
    moves = [(0,0), (1,1), (2,2), (3,3)]
    for r, c in moves:
        game.make_move(r, c, PLAYER_X)
        game.make_move(r, c+1, PLAYER_O) # O đánh lệch sang phải 1 ô
        
    game.make_move(4, 4, PLAYER_X)
    assert game.winner == PLAYER_X

def test_invalid_move():
    game = CaroGame()
    game.make_move(5, 5, PLAYER_X)
    
    # O cố tình đánh đè lên ô (5, 5) của X
    success, msg = game.make_move(5, 5, PLAYER_O)
    
    assert success is False
    assert msg == "Nước đi không hợp lệ."
    assert game.board[5][5] == PLAYER_X # Ô đó vẫn phải là của X