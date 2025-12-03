"""Go game module.

Provides a small `GoGame` subclass with support for passing via `pass_turn`.
This implementation is intentionally minimal and suitable as a template or
for basic unit tests; it doesn't implement captures or scoring.
"""

from __future__ import annotations

from src.core.game import Game, GameStatus
from src.core.board import Board
from src.core.player import Player
from typing import List, Set, Tuple


class GoGame(Game):
	"""Tiny Go game subclass.

	For tests and demo, `make_move` places a stone and `pass_turn` is enabled.
	The class does not implement capture or scoring; it exists to validate
	the factory and base game behavior.
	"""

	def __init__(self, size: int, black_player: Player, white_player: Player):
		board = Board(size)
		super().__init__(board, black_player, white_player)
		# number of stones captured (stones taken off the board) by each side
		self.captured_black: int = 0
		self.captured_white: int = 0
		# consecutive passes count; two consecutive passes ends the game
		self._consecutive_passes: int = 0

	def make_move(self, row: int, col: int) -> None:
		if self.is_over():
			raise ValueError("Game is already over")

		if self.board.get_piece(row, col) != self.board.EMPTY:
			raise ValueError("Position already occupied")

		# record current captured counts and consecutive passes for undo
		prev_captured_black = self.captured_black
		prev_captured_white = self.captured_white
		prev_consecutive_passes = self._consecutive_passes

		# place the stone and record history using base helper
		self._apply_move(row, col)

		# mover is the player that just moved (other_player because _apply_move switched)
		mover_color = self.other_player.color
		opponent_color = self.current_player.color

		# perform captures: any adjacent opponent chains without liberties
		captured_positions: List[Tuple[int, int, str]] = []
		processed_positions: Set[Tuple[int, int]] = set()
		for nr, nc in self._neighbors(row, col):
			if self.board.get_piece(nr, nc) == opponent_color:
				chain = self._find_chain(nr, nc)
				if not self._chain_has_liberties(chain):
					# Skip chains we've already captured from a different neighbor
					if any(pos in processed_positions for pos in chain):
						continue
					# capture the entire chain
					for (r, c) in chain:
						captured_positions.append((r, c, opponent_color))
						# remove from board
						self.board._grid[r][c] = self.board.EMPTY
					processed_positions.update(chain)
					# increment captured counters for mover
					if opponent_color == "black":
						self.captured_white += len(chain)
					else:
						self.captured_black += len(chain)

		# augment history entry with captured information and previous counts
		last = self._history[-1]
		last["captured"] = captured_positions
		last["prev_captured_black"] = prev_captured_black
		last["prev_captured_white"] = prev_captured_white
		last["prev_consecutive_passes"] = prev_consecutive_passes

		# if capture occurred, consecutive passes reset to 0; otherwise also reset because it's a move
		self._consecutive_passes = 0

		# if no captured positions and mover's chain has no liberties -> suicide
		# find chain of the placed stone (mover_color)
		mover_chain = self._find_chain(row, col)
		if not self._chain_has_liberties(mover_chain) and not captured_positions:
			# undo the move and raise
			self.undo()
			raise ValueError("Suicide is not allowed")

		# if board is full -> end by counting
		if not any(
			self.board.get_piece(r, c) == self.board.EMPTY
			for r in range(self.board.get_size())
			for c in range(self.board.get_size())
		):
			self._end_game_by_counts()

	def pass_turn(self) -> None:
		if self.is_over():
			raise ValueError("Game is already over")
		prev_consecutive = self._consecutive_passes
		self._apply_pass()
		self._consecutive_passes += 1
		# record previous consecutive passes for undo
		self._history[-1]["prev_consecutive_passes"] = prev_consecutive
		# if both players have passed consecutively, end game
		if self._consecutive_passes >= 2:
			self._end_game_by_counts()

	def _end_game_by_counts(self) -> None:
		"""Determine winner by counting stones on board + captured stones."""
		black_on_board = 0
		white_on_board = 0
		size = self.board.get_size()
		for r in range(size):
			for c in range(size):
				v = self.board.get_piece(r, c)
				if v == "black":
					black_on_board += 1
				elif v == "white":
					white_on_board += 1
		black_total = black_on_board + self.captured_black
		white_total = white_on_board + self.captured_white
		if black_total > white_total:
			self.status = GameStatus.BLACK_WIN
		elif white_total > black_total:
			self.status = GameStatus.WHITE_WIN
		else:
			self.status = GameStatus.DRAW

	def _neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
		size = self.board.get_size()
		res: List[Tuple[int, int]] = []
		for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
			r, c = row + dr, col + dc
			if 0 <= r < size and 0 <= c < size:
				res.append((r, c))
		return res

	def _find_chain(self, row: int, col: int) -> Set[Tuple[int, int]]:
		"""Return a set of coordinates belonging to a chain connected to (row,col)."""
		color = self.board.get_piece(row, col)
		if color == self.board.EMPTY:
			return set()
		size = self.board.get_size()
		stack = [(row, col)]
		visited: Set[Tuple[int, int]] = set()
		while stack:
			r, c = stack.pop()
			if (r, c) in visited:
				continue
			visited.add((r, c))
			for nr, nc in self._neighbors(r, c):
				if self.board.get_piece(nr, nc) == color and (nr, nc) not in visited:
					stack.append((nr, nc))
		return visited

	def _chain_has_liberties(self, chain: Set[Tuple[int, int]]) -> bool:
		for (r, c) in chain:
			for nr, nc in self._neighbors(r, c):
				if self.board.get_piece(nr, nc) == self.board.EMPTY:
					return True
		return False

	def undo(self) -> None:
		"""Undo with Go-specific restoration of captured stones and counters."""
		if not self._history:
			raise ValueError("No actions to undo")
		entry = self._history.pop()
		action = entry.get("action")
		# restore players and status
		self.current_player = entry.get("previous_current", self.current_player)
		self.other_player = entry.get("previous_other", self.other_player)
		self.status = entry.get("previous_status", self.status)
		if action == "move":
			row = entry["row"]
			col = entry["col"]
			prev = entry["prev_value"]
			# restore position
			if prev == self.board.EMPTY:
				self.board._grid[row][col] = self.board.EMPTY
			else:
				self.board._grid[row][col] = prev
			# restore captured stones and counters
			captured = entry.get("captured", [])
			for r, c, color in captured:
				self.board._grid[r][c] = color
			self.captured_black = entry.get("prev_captured_black", self.captured_black)
			self.captured_white = entry.get("prev_captured_white", self.captured_white)
			self._consecutive_passes = entry.get("prev_consecutive_passes", self._consecutive_passes)
		elif action == "pass":
			# restore consecutive passes
			self._consecutive_passes = entry.get("prev_consecutive_passes", self._consecutive_passes)
		elif action == "resign":
			# nothing else
			pass
		else:
			pass

