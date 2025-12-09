"""Gomoku (Five-in-a-Row) game module.

Provides a minimal `GomokuGame` implementation deriving from `Game`.
This implementation is intentionally simple: it uses the base class helpers
to place moves and does not implement win detection. It is suitable as a
starting point and for the factory tests.
"""

from __future__ import annotations

from typing import Tuple

from src.core.board import Board
from src.core.game import Game, GameStatus
from src.core.player import Player


class GomokuGame(Game):
	"""Gomoku game with simple five-in-a-row detection.

	Constructor accepts `size` and two players, and it constructs the board
	internally. The `make_move` method uses the base class helpers to apply
	moves and maintain history; after each move it checks whether the move
	produces a five-in-a-row for the player who moved.
	"""

	def __init__(self, size: int, black_player: Player, white_player: Player):
		if not isinstance(size, int) or size <= 0:
			raise ValueError("size must be a positive integer")
		board = Board(size)
		super().__init__(board, black_player, white_player)

	def make_move(self, row: int, col: int) -> None:
		if self.is_over():
			raise ValueError("Game is already over")
		# apply the move via base helper (records history and switches turns)
		self._apply_move(row, col)
		# the player who just moved is other_player after the swap
		mover_color = self.other_player.color
		if self._has_five_in_a_row(row, col, mover_color):
			self.status = (
				GameStatus.BLACK_WIN if mover_color == "black" else GameStatus.WHITE_WIN
			)
			return
		# check draw: board full
		if all(
			self.board.get_piece(r, c) != self.board.EMPTY
			for r in range(self.board.get_size())
			for c in range(self.board.get_size())
		):
			self.status = GameStatus.DRAW

	def _has_five_in_a_row(self, row: int, col: int, color: str) -> bool:
		"""Return True if a five-in-a-row exists through (row, col) for color.

		We check four directions: horizontal, vertical, and two diagonals
		by counting consecutive cells of the same color in both directions.
		"""
		size = self.board.get_size()

		def count_in_dir(dr: int, dc: int) -> int:
			r, c = row + dr, col + dc
			count = 0
			while 0 <= r < size and 0 <= c < size and self.board.get_piece(r, c) == color:
				count += 1
				r += dr
				c += dc
			return count

		# directions: (dr,dc) pairs - we will count both directions for each
		directions: Tuple[Tuple[int, int], ...] = ((0, 1), (1, 0), (1, 1), (1, -1))
		for dr, dc in directions:
			total = 1 + count_in_dir(dr, dc) + count_in_dir(-dr, -dc)
			if total >= 5:
				return True
		return False


