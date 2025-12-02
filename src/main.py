"""
主入口：棋类对战平台的简单命令行菜单示例。
"""

from __future__ import annotations

import sys


def _print_menu() -> None:
	"""打印主菜单选项。"""
	print('\n请选择操作：')
	print('1. 开始新游戏')
	print('2. 退出')


def main() -> None:
	"""程序入口。

	启动后在命令行显示欢迎信息并显示一个简单菜单：
	1 -> 打印“新游戏功能正在开发中”
	2 -> 退出程序
	"""
	print('欢迎来到棋类对战平台！\n')

	while True:
		_print_menu()
		try:
			choice = input('输入选项编号并回车: ').strip()
		except (KeyboardInterrupt, EOFError):
			# 若按下 Ctrl+C / Ctrl+D，直接优雅退出
			print('\n已取消，正在退出。')
			sys.exit(0)

		if choice == '1':
			print('\n新游戏功能正在开发中\n')
			# 这里未来可以扩展进入游戏创建的逻辑
			continue
		if choice == '2':
			print('\n谢谢使用，再见！')
			sys.exit(0)

		print('\n无效的选项，请输入 1 或 2。')


if __name__ == '__main__':
	main()

