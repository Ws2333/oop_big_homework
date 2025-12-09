"""Tkinter GUI 客户端入口。

运行：
    python -m src.gui_client

此模块不修改后端逻辑，仅调用 `GameFactory`、`Game` 实例与 `serialization` 工具。
"""

from __future__ import annotations

import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from typing import Optional

from src.core.factory import GameFactory
from src.core.serialization import save_game, load_game


class GUIClient:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("棋类对战平台 (GUI)")

        self.game = None
        self.factory = GameFactory()

        # UI elements
        self.status_var = tk.StringVar()
        self.canvas = None
        self.cell_size = 40
        self.board_size = 9

        self._build_menu()
        self._build_status()
        self._build_board_canvas()
        self._build_controls()

        # 先进入游戏选择界面
        self._show_start_dialog()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="重开游戏", command=self._show_start_dialog)
        game_menu.add_command(label="保存", command=self._on_save)
        game_menu.add_command(label="加载", command=self._on_load)
        game_menu.add_separator()
        game_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=game_menu)
        self.root.config(menu=menubar)

    def _build_status(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, padx=6, pady=4)
        tk.Label(frame, text="当前状态:").pack(side=tk.LEFT)
        tk.Label(frame, textvariable=self.status_var, fg="blue").pack(side=tk.LEFT)

    def _build_board_canvas(self) -> None:
        # canvas 包裹在 frame 中以便自动伸缩
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        self.canvas = tk.Canvas(frame, width=600, height=600, bg="#f5f5dc")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def _build_controls(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, padx=6, pady=6)

        tk.Button(frame, text="悔棋 (Undo)", command=self._on_undo).pack(side=tk.LEFT, padx=4)
        tk.Button(frame, text="过 (Pass)", command=self._on_pass).pack(side=tk.LEFT, padx=4)
        tk.Button(frame, text="认输 (Resign)", command=self._on_resign).pack(side=tk.LEFT, padx=4)
        tk.Button(frame, text="保存 (Save)", command=self._on_save).pack(side=tk.LEFT, padx=4)
        tk.Button(frame, text="加载 (Load)", command=self._on_load).pack(side=tk.LEFT, padx=4)
        tk.Button(frame, text="重开 (Restart)", command=self._show_start_dialog).pack(side=tk.RIGHT, padx=4)

    def _show_start_dialog(self) -> None:
        # 简单对话选择游戏类型与大小
        dlg = tk.Toplevel(self.root)
        dlg.title("开始新游戏")
        dlg.grab_set()

        tk.Label(dlg, text="选择游戏类型:").grid(row=0, column=0, sticky=tk.W, padx=6, pady=6)
        game_type_var = tk.StringVar(value="gomoku")
        tk.Radiobutton(dlg, text="Gomoku (五子棋)", variable=game_type_var, value="gomoku").grid(row=0, column=1, sticky=tk.W)
        tk.Radiobutton(dlg, text="Go (围棋 简化版)", variable=game_type_var, value="go").grid(row=0, column=2, sticky=tk.W)

        tk.Label(dlg, text="棋盘大小:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=6)
        size_var = tk.IntVar(value=15)
        tk.Entry(dlg, textvariable=size_var, width=6).grid(row=1, column=1, sticky=tk.W)

        def _start() -> None:
            t = game_type_var.get()
            s = size_var.get()
            try:
                if s <= 0:
                    raise ValueError("棋盘大小必须为正整数")
                self._start_game(t, int(s))
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("参数错误", str(e))

        tk.Button(dlg, text="开始", command=_start).grid(row=2, column=0, columnspan=3, pady=8)

    def _start_game(self, game_type: str, size: int) -> None:
        try:
            self.game = self.factory.create_game(game_type, size)
        except Exception as e:
            messagebox.showerror("创建游戏失败", str(e))
            return

        self.board_size = self.game.board.get_size()
        self._resize_canvas()
        self._draw_board()
        self._update_status()

    def _resize_canvas(self) -> None:
        # 根据棋盘大小设置单元格与画布大小
        max_pixels = 600
        self.cell_size = max(24, min(60, max_pixels // max(1, self.board_size)))
        canvas_size = self.cell_size * self.board_size
        self.canvas.config(width=canvas_size, height=canvas_size)

    def _draw_board(self) -> None:
        if not self.game:
            return
        b = self.game.board
        n = b.get_size()
        self.canvas.delete("all")

        # 画格子
        for i in range(n + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, n * self.cell_size, fill="#444")
            y = i * self.cell_size
            self.canvas.create_line(0, y, n * self.cell_size, y, fill="#444")

        # 画棋子
        for r in range(n):
            for c in range(n):
                piece = b.get_piece(r, c)
                cx = c * self.cell_size + self.cell_size // 2
                cy = r * self.cell_size + self.cell_size // 2
                if piece == "black":
                    self.canvas.create_text(cx, cy, text="●", font=("Arial", self.cell_size // 2), fill="black")
                elif piece == "white":
                    self.canvas.create_text(cx, cy, text="○", font=("Arial", self.cell_size // 2), fill="black")
                else:
                    # 空位用小点表示
                    self.canvas.create_text(cx, cy, text="·", font=("Arial", max(8, self.cell_size // 3)), fill="#888")

    def _on_canvas_click(self, event) -> None:
        if not self.game:
            return
        # 计算行列
        x, y = event.x, event.y
        col = x // self.cell_size
        row = y // self.cell_size
        n = self.board_size
        if not (0 <= row < n and 0 <= col < n):
            return

        try:
            # 调用后端的 make_move
            self.game.make_move(row, col)
        except Exception as e:
            # 后端会抛出 ValueError 或自定义异常表示非法操作
            messagebox.showwarning("非法落子", str(e))
            return

        self._draw_board()
        self._update_status()
        self._check_game_end()

    def _on_undo(self) -> None:
        if not self.game:
            return
        try:
            self.game.undo()
        except Exception as e:
            messagebox.showwarning("悔棋失败", str(e))
            return
        self._draw_board()
        self._update_status()

    def _on_pass(self) -> None:
        if not self.game:
            return
        try:
            self.game.pass_turn()
        except Exception as e:
            messagebox.showwarning("操作失败", str(e))
            return
        self._draw_board()
        self._update_status()
        self._check_game_end()

    def _on_resign(self) -> None:
        if not self.game:
            return
        try:
            self.game.resign()
        except Exception as e:
            messagebox.showwarning("操作失败", str(e))
            return
        winner = None
        try:
            winner = self.game.get_winner()
        except Exception:
            pass
        messagebox.showinfo("游戏结束", f"玩家认输。胜者: {winner}")
        self._update_status()

    def _on_save(self) -> None:
        if not self.game:
            messagebox.showwarning("保存失败", "当前没有活动游戏")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON 文件", "*.json")])
        if not path:
            return
        try:
            save_game(self.game, path)
            messagebox.showinfo("保存成功", f"已保存到 {os.path.abspath(path)}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _on_load(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON 文件", "*.json")])
        if not path:
            return
        try:
            loaded = load_game(path, self.factory)
            if not loaded:
                raise RuntimeError("加载失败：文件内容无效")
            self.game = loaded
            self.board_size = self.game.board.get_size()
            self._resize_canvas()
            self._draw_board()
            self._update_status()
            messagebox.showinfo("加载成功", f"已从 {os.path.abspath(path)} 恢复游戏")
        except Exception as e:
            messagebox.showerror("加载失败", str(e))

    def _update_status(self) -> None:
        if not self.game:
            self.status_var.set("未开始游戏")
            return
        try:
            cur = getattr(self.game, "current_player", None)
            if cur is None:
                self.status_var.set("无当前玩家")
            else:
                self.status_var.set(str(cur))
        except Exception:
            self.status_var.set("状态不可用")

    def _check_game_end(self) -> None:
        # 检查 is_over / get_winner
        if not self.game:
            return
        try:
            over = getattr(self.game, "is_over", lambda: False)()
            if over:
                winner = None
                try:
                    winner = self.game.get_winner()
                except Exception:
                    winner = None
                messagebox.showinfo("对局结束", f"对局结束。胜者: {winner}")
        except Exception:
            # 不强制依赖这些方法
            pass


def main() -> None:
    root = tk.Tk()
    app = GUIClient(root)
    root.mainloop()


if __name__ == "__main__":
    main()
