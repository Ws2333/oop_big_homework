"""Game base class.

Provides an abstract template for turn-based board games. Game subclasses
implement concrete rules (e.g., Go, Gomoku) by overriding `make_move` and
optionally `pass_turn`.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from src.core.board import Board
from src.core.player import Player


class GameStatus(Enum):
	ONGOING = auto()
	BLACK_WIN = auto()
	WHITE_WIN = auto()
	DRAW = auto()


class Game(abc.ABC):
	"""Abstract game base class.

	Subclasses should implement `make_move` and may override `pass_turn`.
	This base class provides undo via a simple history stack and common
	helpers for subclasses.
	"""

	def __init__(self, board: Board, black_player: Player, white_player: Player):
		self.board = board
		self.black_player = black_player
		self.white_player = white_player
		# default: black moves first
		self.current_player: Player = black_player
		self.other_player: Player = white_player
		self.status: GameStatus = GameStatus.ONGOING
		# history stack for undo: each entry is a dict with enough info
		# to revert a previous action.
		self._history: List[Dict[str, Any]] = []

	# ----- basic helpers and template methods -----
	@abc.abstractmethod
	def make_move(self, row: int, col: int) -> None:
		"""Make a move at (row, col) following game-specific rules.

		Subclasses MUST call protected helpers to record state and apply
		board changes, or handle history themselves.
		"""
		raise NotImplementedError

	def pass_turn(self) -> None:
		"""Pass the turn. By default, games that don't support pass should
		raise NotImplementedError. Subclasses that support passing should
		record history and swap turns.
		"""
		raise NotImplementedError("pass_turn is not supported for this game")

	def resign(self) -> None:
		"""Current player resigns; other player wins. History entry is recorded
		to allow undo.
		"""
		previous_status = self.status
		previous_current = self.current_player
		previous_other = self.other_player
		# record resign action so that undo can restore everything
		self._history.append({
			"action": "resign",
			"previous_status": previous_status,
			"previous_current": previous_current,
			"previous_other": previous_other,
		})
		# set status accordingly
		if self.current_player.color == "black":
			self.status = GameStatus.WHITE_WIN
		else:
			self.status = GameStatus.BLACK_WIN

	def undo(self) -> None:
		"""Undo last action. Restores board, players, and status.

		Raises:
			ValueError: if there is no action to undo.
		"""
		if not self._history:
			raise ValueError("No actions to undo")
		entry = self._history.pop()
		action = entry.get("action")
		# restore players and status always
		self.current_player = entry.get("previous_current", self.current_player)
		self.other_player = entry.get("previous_other", self.other_player)
		self.status = entry.get("previous_status", self.status)

		if action == "move":
			row = entry["row"]
			col = entry["col"]
			prev = entry["prev_value"]
			# restore previous value on board
			# board exposes remove/place; set by direct manipulation
			# we can use board._grid for performance but avoid it; use API:
			if prev == Board.EMPTY:
				# if prev empty, remove piece (set to empty)
				# but Board.remove_piece will raise if already empty; use direct assign
				self.board._grid[row][col] = Board.EMPTY
			else:
				self.board._grid[row][col] = prev
		elif action == "pass":
			# pass had no board changes
			pass
		elif action == "resign":
			# nothing further; status restored above
			pass
		else:
			# unknown action type: ignore
			pass

	def is_over(self) -> bool:
		return self.status != GameStatus.ONGOING

	def get_winner(self) -> Optional[Player]:
		if self.status == GameStatus.BLACK_WIN:
			return self.black_player
		if self.status == GameStatus.WHITE_WIN:
			return self.white_player
		return None

	# ----- protected helpers for subclasses -----
	def _record_move(self, row: int, col: int, prev_value: str) -> None:
		"""Record a move action into history. Subclasses call this before
		or after applying a move depending on their semantics.
		"""
		self._history.append({
			"action": "move",
			"row": row,
			"col": col,
			"prev_value": prev_value,
			"previous_status": self.status,
			"previous_current": self.current_player,
			"previous_other": self.other_player,
		})

	def _apply_move(self, row: int, col: int) -> None:
		"""Apply a simple move: place a piece for current_player and swap turns.

		This helper uses Board.place_piece and will raise whatever exceptions
		board raises (e.g., position occupied).
		"""
		prev = self.board.get_piece(row, col)
		self._record_move(row, col, prev)
		# place the piece
		self.board.place_piece(row, col, self.current_player.color)
		# swap players
		self._switch_turn()

	def _apply_pass(self) -> None:
		"""Apply a pass action: swap players and record history entry."""
		self._history.append({
			"action": "pass",
			"previous_status": self.status,
			"previous_current": self.current_player,
			"previous_other": self.other_player,
		})
		self._switch_turn()

	def _switch_turn(self) -> None:
		self.current_player, self.other_player = self.other_player, self.current_player

