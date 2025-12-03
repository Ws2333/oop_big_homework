"""Go game module.

Provides a small `GoGame` subclass with support for passing via `pass_turn`.
This implementation is intentionally minimal and suitable as a template or
for basic unit tests; it doesn't implement captures or scoring.
"""

from __future__ import annotations

from src.core.game import Game


class GoGame(Game):
	"""Tiny Go game subclass.

	For tests and demo, `make_move` places a stone and `pass_turn` is enabled.
	The class does not implement capture or scoring; it exists to validate
	the factory and base game behavior.
	"""

	def make_move(self, row: int, col: int) -> None:
		# Place stone via base helper.
		self._apply_move(row, col)

	def pass_turn(self) -> None:
		# Support pass in Go
		self._apply_pass()

