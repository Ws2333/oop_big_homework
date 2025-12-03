import unittest

from src.core.board import Board
from src.core.player import Player
from src.core.game import Game, GameStatus


class SimpleGame(Game):
    """A tiny concrete game for testing Base Game behavior.

    It does no win detection. `make_move` simply places a piece by calling
    the base class `_apply_move` helper.
    """

    def make_move(self, row: int, col: int) -> None:
        self._apply_move(row, col)

    def pass_turn(self) -> None:
        # allow pass in this simple game by calling base helper
        self._apply_pass()


class TestGame(unittest.TestCase):
    def setUp(self):
        self.board = Board(3)
        self.black = Player("BlackPlayer", "black")
        self.white = Player("WhitePlayer", "white")
        self.game = SimpleGame(self.board, self.black, self.white)

    def test_simple_move_and_undo(self):
        self.assertEqual(self.game.current_player, self.black)
        self.game.make_move(0, 0)
        # black placed at 0,0
        self.assertEqual(self.board.get_piece(0, 0), "black")
        # turn switched
        self.assertEqual(self.game.current_player, self.white)
        # undo revert placement and current_player
        self.game.undo()
        self.assertEqual(self.board.get_piece(0, 0), "empty")
        self.assertEqual(self.game.current_player, self.black)

    def test_pass_and_undo(self):
        self.assertEqual(self.game.current_player, self.black)
        self.game.pass_turn()
        self.assertEqual(self.game.current_player, self.white)
        self.game.undo()
        self.assertEqual(self.game.current_player, self.black)

    def test_resign_and_undo(self):
        # black resigns
        self.game.resign()
        self.assertTrue(self.game.is_over())
        self.assertEqual(self.game.get_winner(), self.white)
        # undo
        self.game.undo()
        self.assertFalse(self.game.is_over())
        self.assertIsNone(self.game.get_winner())

    def test_pass_default_not_implemented_on_base(self):
        # ensure base class pass_turn raises NotImplementedError
        b = Board(3)
        g = self.game  # SimpleGame overrides pass so it's ok
        # But the base class would raise NotImplementedError; demonstrate that tests
        # call the base method directly to verify behaviour
        with self.assertRaises(NotImplementedError):
            Game.pass_turn(g)


if __name__ == "__main__":
    unittest.main()
