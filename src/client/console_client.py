"""Console client for playing games via command-line.

Provides a simple loop-driven client that uses a GameFactory to create
games and interact with them through commands. Designed to be clear and
easy to read for teaching purposes.
"""

from __future__ import annotations

import json
import os
from typing import Any

from src.core.factory import GameFactory
from src.core.gomoku import GomokuGame
from src.core.go import GoGame
from src.core.board import Board
from src.core.game import Game, GameStatus


class ConsoleClient:
    def __init__(self, factory: GameFactory):
        self.factory = factory

    def run(self) -> None:
        """Run the main client loop."""
        while True:
            print("\n=== 主菜单 ===")
            print("选择游戏类型：1) gomoku  2) go  3) 退出")
            choice = input("输入 1/2/3: ").strip()
            if choice == "3":
                print("退出。")
                return
            if choice not in ("1", "2"):
                print("无效选择，请输入 1、2 或 3。")
                continue

            game_type = "gomoku" if choice == "1" else "go"

            size = self._prompt_board_size()
            if size is None:
                continue

            try:
                game = self.factory.create_game(game_type, size)
            except Exception as e:
                print(f"创建游戏失败: {e}")
                continue

            print(f"已创建 {game_type} {size}x{size} 对局。输入 'help' 查看指令。\n")
            self._game_loop(game, game_type)

    def _prompt_board_size(self) -> int | None:
        while True:
            s = input("请输入棋盘大小 (8-19)，或输入 q 返回主菜单: ").strip()
            if s.lower() == "q":
                return None
            if not s.isdigit():
                print("请输入数字。")
                continue
            size = int(s)
            if size < 8 or size > 19:
                print("大小需在 8 到 19 之间。")
                continue
            return size

    def _game_loop(self, game: Game, game_type: str) -> None:
        while True:
            self._display_board(game.board)
            cur = game.current_player
            print(f"当前轮到: {cur.name} ({cur.color})")
            print("可用命令: move x y | pass | undo | resign | save filename | load filename | restart | help | quit")
            cmd = input("> ").strip()
            if not cmd:
                continue
            parts = cmd.split()
            action = parts[0].lower()

            # 每个命令分别处理常见错误并给出友好提示，保证循环不中断
            if action == "help":
                self._print_help()
            elif action == "move":
                if len(parts) != 3:
                    print("用法: move x y （x 和 y 为从 0 开始的行列索引）")
                    continue
                try:
                    x = int(parts[1])
                    y = int(parts[2])
                except ValueError:
                    print("坐标需为整数。")
                    continue
                try:
                    game.make_move(x, y)
                except ValueError as e:
                    # 包括非法位置、禁手或自杀等由游戏层抛出的错误
                    print(f"落子失败（无效位置或规则不允许）: {e}")
                    continue
                except Exception as e:
                    print(f"落子失败: {e}")
                    continue
            elif action == "pass":
                try:
                    game.pass_turn()
                except NotImplementedError:
                    print("此游戏不支持 pass。")
                except ValueError as e:
                    print(f"pass 失败: {e}")
                except Exception as e:
                    print(f"pass 失败: {e}")
            elif action == "undo":
                try:
                    game.undo()
                except ValueError as e:
                    # 例如没有可悔棋的步数
                    print(f"无法悔棋: {e}")
                except Exception as e:
                    print(f"无法悔棋: {e}")
            elif action == "resign":
                try:
                    game.resign()
                except Exception as e:
                    print(f"认输失败: {e}")
            elif action == "save":
                if len(parts) != 2:
                    print("用法: save filename")
                    continue
                try:
                    self._save_game(game, parts[1], game_type)
                except IOError as e:
                    print(f"保存失败（IO 错误）: {e}")
                except Exception as e:
                    print(f"保存失败: {e}")
            elif action == "load":
                if len(parts) != 2:
                    print("用法: load filename")
                    continue
                try:
                    loaded = self._load_game(parts[1])
                except FileNotFoundError:
                    print("加载失败: 文件不存在。")
                    continue
                except IOError as e:
                    print(f"加载失败（IO 错误）: {e}")
                    continue
                except ValueError as e:
                    print(f"加载失败: {e}")
                    continue
                except Exception as e:
                    print(f"加载失败: {e}")
                    continue

                if loaded is None:
                    print("加载失败。")
                    continue
                game, game_type = loaded
            elif action == "restart":
                print("回到主菜单。")
                return
            elif action == "quit":
                print("退出程序。")
                raise SystemExit
            else:
                print("未知命令，输入 'help' 查看帮助。")

            # check end of game
            if game.is_over():
                self._display_board(game.board)
                winner = game.get_winner()
                if winner:
                    print(f"游戏结束，获胜者：{winner.name} ({winner.color})")
                else:
                    print("游戏结束，和局。")
                print("返回主菜单。\n")
                return

    def _display_board(self, board: Board) -> None:
        size = board.get_size()
        # header
        header = "   " + " ".join(f"{i:2d}" for i in range(size))
        print(header)
        for r in range(size):
            row_str = []
            for c in range(size):
                v = board.get_piece(r, c)
                ch = "."
                if v == "black":
                    ch = "X"
                elif v == "white":
                    ch = "O"
                row_str.append(ch)
            print(f"{r:2d} " + "  ".join(row_str))

    def _print_help(self) -> None:
        print("命令说明:")
        print("  move x y    在 (x,y) 落子，坐标为从 0 开始的行列索引")
        print("  pass        围棋可用，跳过一回合")
        print("  undo        悔棋一步")
        print("  resign      投子认负")
        print("  save f      保存当前局面到文件 f")
        print("  load f      从文件 f 加载局面")
        print("  restart     返回主菜单，重新开始")
        print("  help        显示本帮助")
        print("  quit        退出程序")

    def _save_game(self, game: Game, filename: str, game_type: str) -> None:
        data: dict[str, Any] = {}
        data["game_type"] = game_type
        data["size"] = game.board.get_size()
        data["black_name"] = game.black_player.name
        data["white_name"] = game.white_player.name
        data["current_color"] = game.current_player.color
        data["status"] = game.status.name
        # board grid
        size = game.board.get_size()
        grid = [[game.board.get_piece(r, c) for c in range(size)] for r in range(size)]
        data["grid"] = grid
        # go-specific data
        if isinstance(game, GoGame):
            data["captured_black"] = game.captured_black
            data["captured_white"] = game.captured_white
            # consecutive passes
            data["consecutive_passes"] = getattr(game, "_consecutive_passes", 0)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"已保存到 {filename}")
        except Exception as e:
            print(f"保存失败: {e}")

    def _load_game(self, filename: str) -> tuple[Game, str] | None:
        if not os.path.exists(filename):
            print("文件不存在：", filename)
            return None
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None

        game_type = data.get("game_type")
        size = data.get("size")
        if game_type not in ("gomoku", "go") or not isinstance(size, int):
            print("文件格式不正确。")
            return None

        try:
            game = self.factory.create_game(game_type, size)
        except Exception as e:
            print(f"创建游戏失败: {e}")
            return None

        # reset board by placing pieces according to saved grid
        grid = data.get("grid", [])
        # clear any existing stones (new game is empty) and place
        for r in range(size):
            for c in range(size):
                v = grid[r][c]
                if v == Board.EMPTY:
                    continue
                try:
                    game.board.place_piece(r, c, v)
                except Exception as e:
                    print(f"加载时设置格子失败 ({r},{c}): {e}")
                    return None

        # restore meta state
        cur_color = data.get("current_color")
        if cur_color == game.black_player.color:
            game.current_player = game.black_player
            game.other_player = game.white_player
        else:
            game.current_player = game.white_player
            game.other_player = game.black_player

        status_name = data.get("status")
        try:
            game.status = GameStatus[status_name]
        except Exception:
            game.status = GameStatus.ONGOING

        if isinstance(game, GoGame):
            game.captured_black = int(data.get("captured_black", 0))
            game.captured_white = int(data.get("captured_white", 0))
            game._consecutive_passes = int(data.get("consecutive_passes", 0))

        print(f"已从 {filename} 加载局面。")
        return game, game_type
