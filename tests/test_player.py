import unittest

from src.core.player import Player


class TestPlayer(unittest.TestCase):
    def test_str_and_fields(self):
        p = Player("Alice", "black")
        self.assertEqual(str(p), "Alice (black)")
        self.assertEqual(p.name, "Alice")
        self.assertEqual(p.color, "black")

    def test_invalid_name(self):
        with self.assertRaises(ValueError):
            Player("", "white")
        with self.assertRaises(ValueError):
            Player(123, "white")  # type: ignore

    def test_invalid_color(self):
        with self.assertRaises(ValueError):
            Player("Bob", "green")


if __name__ == "__main__":
    unittest.main()
