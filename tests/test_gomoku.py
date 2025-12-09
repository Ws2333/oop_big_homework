import unittest

from src.core.gomoku import GomokuGame
from src.core.player import Player
from src.core.game import GameStatus


def play_sequence(game, moves):
    """Helper: play moves in order. Each entry is (r, c)."""
    for r, c in moves:
        game.make_move(r, c)


class TestGomoku(unittest.TestCase):
    def setUp(self):
        self.black = Player("B", "black")
        self.white = Player("W", "white")

    def test_horizontal_win(self):
        g = GomokuGame(5, self.black, self.white)
        # alternate moves so black places at (0,0)-(0,4)
        moves = [
            (0, 0), (4, 4),
            (0, 1), (4, 3),
            (0, 2), (4, 2),
            (0, 3), (4, 1),
            (0, 4)
        ]
        play_sequence(g, moves)
        self.assertTrue(g.is_over())
        self.assertEqual(g.status, GameStatus.BLACK_WIN)
        self.assertEqual(g.get_winner(), self.black)

    def test_vertical_win(self):
        g = GomokuGame(5, self.black, self.white)
        moves = [
            (0, 0), (4, 4),
            (1, 0), (4, 3),
            (2, 0), (4, 2),
            (3, 0), (4, 1),
            (4, 0)
        ]
        play_sequence(g, moves)
        self.assertEqual(g.status, GameStatus.BLACK_WIN)

    def test_diagonal_win(self):
        g = GomokuGame(5, self.black, self.white)
        moves = [
            (0, 0), (4, 4),
            (1, 1), (4, 3),
            (2, 2), (4, 2),
            (3, 3), (4, 1),
            (4, 4)
        ]
        # Note: last move duplicates a white move in dummy zone; adjust last for black
        moves[-1] = (4, 4)  # black final move at (4,4)
        # But (4,4) already used by white as first green move; to ensure not occupied, change white dummy placements
        # Rebuild moves with white placed at safe spots (3,4), (3,3), (3,2), (3,1)
        g = GomokuGame(5, self.black, self.white)
        moves = [
            (0, 0), (3, 4),
            (1, 1), (3, 3),
            (2, 2), (3, 2),
            (3, 3), (3, 1),
            (4, 4)
        ]
        # Adjust: ensure not placing on same spot; instead use distinct safe white moves
        g = GomokuGame(5, self.black, self.white)
        moves = [
            (0, 0), (4, 0),
            (1, 1), (4, 1),
            (2, 2), (4, 2),
            (3, 3), (4, 3),
            (4, 4)
        ]
        play_sequence(g, moves)
        self.assertEqual(g.status, GameStatus.BLACK_WIN)

    def test_draw(self):
        g = GomokuGame(3, self.black, self.white)
        # fill the 3x3 board without five in a row
        moves = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2)
        ]
        play_sequence(g, moves)
        self.assertTrue(g.is_over())
        self.assertEqual(g.status, GameStatus.DRAW)

    def test_undo(self):
        g = GomokuGame(5, self.black, self.white)
        # set up 4 in a row and then the winning move
        moves = [
            (0, 0), (4, 4),
            (0, 1), (4, 3),
            (0, 2), (4, 2),
            (0, 3), (4, 1),
            (0, 4)
        ]
        play_sequence(g, moves)
        self.assertEqual(g.status, GameStatus.BLACK_WIN)
        # undo the winning move
        g.undo()
        self.assertEqual(g.status, GameStatus.ONGOING)
        self.assertEqual(g.get_winner(), None)
        self.assertEqual(g.board.get_piece(0, 4), "empty")


if __name__ == "__main__":
    unittest.main()
