import unittest

from src.core.board import Board, InvalidPositionError, PositionOccupiedError


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(3)

    def test_get_size_and_empty(self):
        self.assertEqual(self.board.get_size(), 3)
        # all cells must be 'empty'
        for r, c in self.board.iter_positions():
            self.assertEqual(self.board.get_piece(r, c), "empty")

    def test_place_and_get_piece(self):
        self.board.place_piece(1, 1, "black")
        self.assertEqual(self.board.get_piece(1, 1), "black")

    def test_place_invalid_color(self):
        with self.assertRaises(ValueError):
            self.board.place_piece(0, 0, "green")

    def test_place_on_occupied(self):
        self.board.place_piece(0, 2, "white")
        with self.assertRaises(PositionOccupiedError):
            self.board.place_piece(0, 2, "black")

    def test_remove_piece(self):
        self.board.place_piece(2, 2, "white")
        self.board.remove_piece(2, 2)
        self.assertEqual(self.board.get_piece(2, 2), "empty")

    def test_remove_empty_raises(self):
        with self.assertRaises(ValueError):
            self.board.remove_piece(0, 0)

    def test_invalid_position_raises(self):
        with self.assertRaises(InvalidPositionError):
            self.board.get_piece(-1, 0)
        with self.assertRaises(InvalidPositionError):
            self.board.place_piece(3, 3, "black")
        with self.assertRaises(InvalidPositionError):
            self.board.remove_piece(10, 0)

    def test_iter_positions_count(self):
        coords = list(self.board.iter_positions())
        self.assertEqual(len(coords), self.board.get_size() ** 2)
        self.assertIn((0, 0), coords)
        self.assertIn((2, 2), coords)


if __name__ == "__main__":
    unittest.main()
