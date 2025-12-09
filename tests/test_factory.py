import unittest

from src.core.factory import GameFactory
from src.core.gomoku import GomokuGame
from src.core.go import GoGame


class TestGameFactory(unittest.TestCase):
    def test_gomoku_created(self):
        game = GameFactory.create_game("gomoku", 15)
        self.assertIsInstance(game, GomokuGame)
        self.assertEqual(game.board.get_size(), 15)

    def test_go_created(self):
        game = GameFactory.create_game("go", 9)
        self.assertIsInstance(game, GoGame)
        self.assertEqual(game.board.get_size(), 9)

    def test_game_type_case_insensitive(self):
        game = GameFactory.create_game("Go", 5)
        self.assertIsInstance(game, GoGame)

    def test_unknown_game_type(self):
        with self.assertRaises(ValueError):
            GameFactory.create_game("chess", 8)


if __name__ == "__main__":
    unittest.main()
