"""Gomoku (Five-in-a-Row) game module.

Provides a minimal `GomokuGame` implementation deriving from `Game`.
This implementation is intentionally simple: it uses the base class helpers
to place moves and does not implement win detection. It is suitable as a
starting point and for the factory tests.
"""

from __future__ import annotations

from src.core.game import Game


class GomokuGame(Game):
	"""Very small Gomoku game subclass for demo/tests.

	This game uses `_apply_move` to place stones and swap turns. No win
	detection or advanced rules are implemented here.
	"""

	def make_move(self, row: int, col: int) -> None:
		# Gomoku: place a stone and switch turns
		self._apply_move(row, col)

