"""Game factory module.

Provides a simple factory function for creating different game types.
The create_game method follows a simple factory pattern, centralizing
construction logic and making it easy to add new game types later.
"""

from __future__ import annotations

from typing import Type

from src.core.board import Board
from src.core.player import Player
from src.core.game import Game

# Imports for concrete games
from src.core.gomoku import GomokuGame
from src.core.go import GoGame


class GameFactory:
	"""Create game instances by type using a simple factory.

	Usage:
		game = GameFactory.create_game('gomoku', 15)
	"""

	_registry = {
		"gomoku": GomokuGame,
		"go": GoGame,
	}

	@staticmethod
	def create_game(game_type: str, size: int) -> Game:
		"""Create a game instance based on game_type.

		Args:
			game_type: Either 'gomoku' or 'go'. Case-insensitive.
			size: Board size to create.
		Raises:
			ValueError: if an unknown game_type is provided.
		"""
		normalized = (game_type or "").strip().lower()
		game_cls: Type[Game] = GameFactory._registry.get(normalized)
		if game_cls is None:
			raise ValueError(f"Unknown game type: {game_type}")
		# create two default players: Black and White
		black = Player("Black", "black")
		white = Player("White", "white")
		return game_cls(size, black, white)

