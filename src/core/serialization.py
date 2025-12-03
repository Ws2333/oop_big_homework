"""Simple game serialization helpers.

Provides save_game and load_game using JSON. The format is intentionally
simple and stores:
 - game_type: "gomoku" or "go"
 - size: board size
 - grid: 2D array of strings ('empty'/'black'/'white')
 - current_color: which color should play next ('black' or 'white')
 - optional: status and Go-specific captured counters and consecutive passes

These helpers are designed to be easy to read and call from the
command-line client.
"""

from __future__ import annotations

import json
import os
from typing import Any

from src.core.factory import GameFactory
from src.core.game import Game, GameStatus
from src.core.board import Board
from src.core.go import GoGame


def save_game(game: Game, filename: str) -> None:
    """Save minimal game state to `filename` in JSON.

    The saved data includes game type, size, grid and which color moves next.
    For Go games we also save captured counts and consecutive passes when
    available.
    """
    data: dict[str, Any] = {}
    # Try to infer game type from class name or instance
    game_type = getattr(game, "__class__", None).__name__.lower()
    # normalize to expected tokens
    if "gomoku" in game_type:
        data["game_type"] = "gomoku"
    elif "go" in game_type:
        data["game_type"] = "go"
    else:
        # fallback: require GameFactory compatibility; try attribute
        data["game_type"] = getattr(game, "game_type", "unknown")

    size = game.board.get_size()
    data["size"] = size
    data["current_color"] = game.current_player.color
    data["status"] = getattr(game, "status", GameStatus.ONGOING).name

    # grid
    grid = [[game.board.get_piece(r, c) for c in range(size)] for r in range(size)]
    data["grid"] = grid

    # Go-specific fields
    if isinstance(game, GoGame):
        data["captured_black"] = getattr(game, "captured_black", 0)
        data["captured_white"] = getattr(game, "captured_white", 0)
        data["consecutive_passes"] = getattr(game, "_consecutive_passes", 0)

    # write file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_game(filename: str, factory: GameFactory) -> Game:
    """Load a game from `filename` and return a Game instance created by factory.

    The factory is used to create the right Game subclass; after creation the
    board and current player are restored according to the file. Raises
    FileNotFoundError or ValueError on invalid input.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    game_type = data.get("game_type")
    size = data.get("size")
    grid = data.get("grid")
    cur_color = data.get("current_color")
    status_name = data.get("status")

    if game_type not in ("gomoku", "go"):
        raise ValueError("unsupported game_type in file")
    if not isinstance(size, int) or not isinstance(grid, list):
        raise ValueError("invalid size or grid in file")

    # create new game using factory
    game = factory.create_game(game_type, size)

    # restore board
    for r in range(size):
        for c in range(size):
            val = grid[r][c]
            if val == Board.EMPTY:
                continue
            # place_piece should succeed because new board is empty
            game.board.place_piece(r, c, val)

    # restore current player
    if cur_color == game.black_player.color:
        game.current_player = game.black_player
        game.other_player = game.white_player
    else:
        game.current_player = game.white_player
        game.other_player = game.black_player

    # restore status if present
    try:
        game.status = GameStatus[status_name]
    except Exception:
        game.status = GameStatus.ONGOING

    # restore Go-specific data if present
    if isinstance(game, GoGame):
        game.captured_black = int(data.get("captured_black", 0))
        game.captured_white = int(data.get("captured_white", 0))
        game._consecutive_passes = int(data.get("consecutive_passes", 0))

    return game
