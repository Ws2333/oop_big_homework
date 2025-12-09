"""Board module

Provides a simple Board class for a two-dimensional square board.
This is a lightweight, clear implementation intended as a teaching/example
piece for the Board abstraction used by board games like Go or Gomoku.
"""

from __future__ import annotations

from typing import Generator, List, Tuple


class BoardError(Exception):
	"""Base class for board-related errors."""


class InvalidPositionError(BoardError, IndexError):
	"""Raised when a row/col pair is outside the board bounds."""


class PositionOccupiedError(BoardError, ValueError):
	"""Raised when attempting to place a piece on a non-empty position."""


class Board:
	"""A simple square board.

	The board stores pieces in a 2D list. Each cell contains one of the
	following strings: 'empty', 'black', 'white'. Rows and columns are
	zero-indexed.
	"""

	VALID_COLORS = {"black", "white"}
	EMPTY = "empty"

	def __init__(self, size: int):
		"""Create a size x size board.

		Args:
			size: board dimension (must be >= 1).
		Raises:
			ValueError: if size is not a positive integer.
		"""
		if not isinstance(size, int) or size <= 0:
			raise ValueError("size must be a positive integer")
		self._size: int = size
		# initialize a 2D list of 'empty'
		self._grid: List[List[str]] = [
			[self.EMPTY for _ in range(size)] for _ in range(size)
		]

	def get_size(self) -> int:
		"""Return the board side length (number of rows/cols)."""
		return self._size

	def _validate_position(self, row: int, col: int) -> None:
		"""Internal: validate that the (row, col) pair is on-board.

		Raises InvalidPositionError if the coordinate is out of range.
		"""
		if not (0 <= row < self._size and 0 <= col < self._size):
			raise InvalidPositionError(f"Position ({row}, {col}) is out of bounds")

	def get_piece(self, row: int, col: int) -> str:
		"""Return the piece at (row, col) as 'empty', 'black', or 'white'.

		Raises InvalidPositionError for out-of-range coordinates.
		"""
		self._validate_position(row, col)
		return self._grid[row][col]

	def place_piece(self, row: int, col: int, color: str) -> None:
		"""Place a piece of `color` at (row, col). Valid colors: 'black', 'white'.

		Raises:
			InvalidPositionError: if the (row, col) is out of bounds.
			ValueError: if the color is invalid.
			PositionOccupiedError: if the position is already occupied.
		"""
		self._validate_position(row, col)
		if color not in self.VALID_COLORS:
			raise ValueError(f"Invalid color '{color}'. Valid colors: {self.VALID_COLORS}")
		if self._grid[row][col] != self.EMPTY:
			raise PositionOccupiedError(f"Position ({row}, {col}) is already occupied")
		self._grid[row][col] = color

	def remove_piece(self, row: int, col: int) -> None:
		"""Remove a piece at (row, col), setting the cell to 'empty'.

		Raises InvalidPositionError if out-of-range.
		Raises ValueError if the cell is already empty.
		"""
		self._validate_position(row, col)
		if self._grid[row][col] == self.EMPTY:
			raise ValueError(f"Cannot remove piece: position ({row}, {col}) is already empty")
		self._grid[row][col] = self.EMPTY

	def iter_positions(self) -> Generator[Tuple[int, int], None, None]:
		"""Yield all board coordinates as (row, col) pairs in row-major order.

		Example:
			for r, c in board.iter_positions():
				# do something with (r, c)
		"""
		for r in range(self._size):
			for c in range(self._size):
				yield (r, c)

	def __repr__(self) -> str:
		"""Human-readable representation; useful for debugging and teaching.

		Very small board prints the grid in a compact form.
		"""
		rows = [" ".join(self._grid[r]) for r in range(self._size)]
		return f"Board(size={self._size})\n" + "\n".join(rows)

