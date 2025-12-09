import unittest

from src.core.player import Player
from src.core.go import GoGame
from src.core.game import GameStatus


def play_sequence(game, moves):
    for r, c in moves:
        game.make_move(r, c)


class TestGoGame(unittest.TestCase):
    def setUp(self):
        self.black = Player("B", "black")
        self.white = Player("W", "white")

    def test_capture_simple(self):
        g = GoGame(3, self.black, self.white)
        moves = [
            (1, 1),  # B - center
            (1, 0),  # W
            (0, 0),  # B
            (0, 1),  # W
            (0, 2),  # B
            (1, 2),  # W
            (2, 2),  # B
            (2, 1),  # W -> should capture B(1,1)
        ]
        play_sequence(g, moves)
        self.assertEqual(g.board.get_piece(1, 1), "empty")
        # White captured 1 black stone
        self.assertEqual(g.captured_white, 4)

    def test_suicide_illegal(self):
        g = GoGame(3, self.black, self.white)
        moves = [
            (0, 0),
            (1, 0),
            (0, 2),
            (0, 1),
            (2, 0),
            (1, 2),
            (2, 2),
            (2, 1),
        ]
        # after these moves, the center (1,1) is surrounded by white stones
        play_sequence(g, moves)
        with self.assertRaises(ValueError):
            g.make_move(1, 1)  # black attempts suicide

    def test_pass_end_and_winner_count(self):
        g = GoGame(3, self.black, self.white)
        # set black advantage
        g.make_move(0, 0)  # B
        g.make_move(0, 1)  # W
        g.make_move(1, 0)  # B
        g.make_move(1, 1)  # W
        g.make_move(2, 0)  # B (black now has 3 stones vs white 2)
        g.pass_turn()  # W pass
        g.pass_turn()  # B pass -> end
        self.assertTrue(g.is_over())
        self.assertEqual(g.status, GameStatus.BLACK_WIN)

    def test_undo_with_capture(self):
        g = GoGame(3, self.black, self.white)
        moves = [
            (1, 1),
            (1, 0),
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (2, 1),
        ]
        play_sequence(g, moves)
        self.assertEqual(g.captured_white, 4)
        self.assertEqual(g.board.get_piece(1, 1), "empty")
        g.undo()  # undo the last white move which captured B
        # after undo, the last captured stones by the last move should be restored
        # earlier captures (0,0) and (0,2) remain removed
        self.assertEqual(g.captured_white, 2)
        # the stones captured on the last move should be restored
        self.assertEqual(g.board.get_piece(1, 1), "black")
        self.assertEqual(g.board.get_piece(2, 2), "black")
        # earlier captured stones remain empty
        self.assertEqual(g.board.get_piece(0, 0), "empty")
        self.assertEqual(g.board.get_piece(0, 2), "empty")


if __name__ == "__main__":
    unittest.main()
