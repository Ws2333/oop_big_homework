from __future__ import annotations
"""
主入口：棋类对战平台的简单命令行菜单示例。
"""

import sys
from typing import NoReturn

from src.client.console_client import ConsoleClient
from src.core.factory import GameFactory


def _print_menu() -> None:
    """打印主菜单选项。"""
    print("\n请选择操作：")
    print("1. 开始新游戏")
    print("2. 退出")


def _exit(message: str = "谢谢使用，再见！") -> NoReturn:
    """优雅退出程序。"""
    print(f"\n{message}")
    sys.exit(0)


def main() -> None:
    """程序入口：显示主菜单并处理用户选择。"""
    print("欢迎来到棋类对战平台！\n")

    while True:
        _print_menu()
        try:
            choice = input("输入选项编号并回车: ").strip()
        except (KeyboardInterrupt, EOFError):
            _exit("已取消，正在退出。")

        if choice == "1":
            try:
                client = ConsoleClient(GameFactory())
                client.run()
            except Exception as exc:
                print(f"运行游戏时发生错误：{exc}")
            continue

        if choice == "2":
            _exit()

        print("\n无效的选项，请输入 1 或 2。")


if __name__ == "__main__":
    main()
