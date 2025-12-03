# 第一阶段设计文档

本文面向教师与指导者，说明“棋类对战平台”项目第一阶段的整体设计。文档重点阐述面向对象设计思想、主要类与职责、采用的设计模式、模块分层（前后端分离）以及教学价值与扩展方向。语言力求清晰正式，便于课堂评审与归档。

---

## 1. 概述

本项目为一个教学用的棋类对战平台（命令行实现），第一阶段目标是实现可运行的核心逻辑（支持 Gomoku 与简化版 Go）、一个命令行客户端、基本的保存/加载以及单元测试覆盖。设计原则为面向对象、职责单一、模块化以便扩展与替换前端。

关键交付物：核心类（Board、Player、Game 抽象、GomokuGame、GoGame）、工厂（GameFactory）、序列化（save/load）、命令行客户端（ConsoleClient）和相关单元测试。

---

## 2. 项目目录（概要）

```
README.md
docs/
	design_phase1.md
src/
	__init__.py
	main.py
	client/
		console_client.py
	core/
		board.py
		player.py
		game.py
		gomoku.py
		go.py
		factory.py
		serialization.py
tests/
	test_board.py
	test_player.py
	test_game.py
	test_gomoku.py
	test_go.py
	test_factory.py
```

（注：测试文件为本阶段示例，覆盖核心逻辑的关键路径）

---

## 3. 设计目标与约束

- 教学优先：代码清晰、易读、便于展示 OOP 与设计模式。  
- 可扩展：后续可增加更多棋类、AI、GUI 或网络对战。  
- 简化规则：围棋为教学版（实现提子、自杀与简化计分）；五子棋实现五连胜检测。  
- 可测性：模块化设计，方便单元测试。  

---

## 4. 面向对象设计要点

- 抽象（Abstraction）：使用 `Game` 抽象共性行为（落子、过、悔棋、判胜），子类实现具体规则。  
- 封装（Encapsulation）：`Board`、`Game` 等隐藏内部实现，提供清晰的公开方法（`place_piece`/`get_piece`/`remove_piece` 等）。  
- 单一职责（SRP）：每个类职责明确，避免臃肿。  
- 依赖注入与接口隔离：`ConsoleClient` 接受 `GameFactory`，通过工厂构建游戏，减少耦合，便于测试替换实现。  

---

## 5. 主要类与职责

以下按模块列出主要类与功能要点：

- `Board` (`src/core/board.py`)  
	- 职责：管理棋盘状态（size x size）。  
	- 数据：二维列表保存每格状态 `'empty'|'black'|'white'`。  
	- 方法：`get_size()`、`get_piece(row,col)`、`place_piece(row,col,color)`（位置越界/被占抛异常）、`remove_piece(row,col)`、`iter_positions()`。  

- `Player` (`src/core/player.py`)  
	- 职责：表示玩家（姓名、颜色），提供可读的 `__str__`。  

- `Game`（抽象基类，`src/core/game.py`）  
	- 职责：定义回合制棋类的公共接口与行为骨架。  
	- 属性：`board`、`black_player`、`white_player`、`current_player`、`other_player`、`status`（枚举 `GameStatus`）、历史栈 `_history`（用于 `undo`）。  
	- 抽象方法：`make_move(row,col)`（子类实现）。  
	- 模板/工具方法：`_apply_move()`、`_apply_pass()`、`_record_move()`、`_switch_turn()` 等用于子类复用。  
	- 其它：`pass_turn()`（默认不支持）、`resign()`、`undo()`、`is_over()`、`get_winner()`。  

- `GomokuGame` (`src/core/gomoku.py`)  
	- 职责：五子棋规则实现（五连胜判定）。  
	- 行为：`make_move` 使用 `_apply_move` 放子并检查是否形成横/竖/对角的五连；若棋盘满且无胜者则判平局。  

- `GoGame` (`src/core/go.py`)（简化围棋）  
	- 职责：围棋规则（教学版）。  
	- 行为（简化规则实现，教学友好）：  
		- 提子（若对方相邻链无气则移除）、禁止自杀（若落子后自家无气且未吃子则非法）；  
		- `pass_turn()` 支持并记录连续过手计数；双方连续各 pass 一次或棋盘无空位时结束；  
		- 以“棋盘上子 + 被提子”总数判断胜负（简化计分）；  
	- 维护：`captured_black`、`captured_white`、`_consecutive_passes`。  

- `GameFactory` (`src/core/factory.py`)  
	- 设计模式：工厂模式（Simple Factory）。  
	- 功能：`create_game(game_type: str, size: int)`，根据 `game_type` 返回相应 Game 实例（GomokuGame 或 GoGame）。  

- `serialization` (`src/core/serialization.py`)  
	- 功能：`save_game(game, filename)` 与 `load_game(filename, factory)`，使用 JSON 保存/加载棋盘、当前方、游戏类型与 Go 特定字段（捕获计数、连续过手）。  

- `ConsoleClient` (`src/client/console_client.py`)  
	- 职责：提供命令行交互界面（主菜单、对局循环、命令解析与显示）。  
	- 命令：`move x y`, `pass`, `undo`, `resign`, `save filename`, `load filename`, `restart`, `help`, `quit`。  
	- 健壮性：客户端捕获常见异常并给出友好提示，保证交互循环不中断。  

---

## 6. 采用的设计模式（明确列举并说明用途）

- 工厂模式（Factory）  
	- 体现：`GameFactory.create_game(...)`。  
	- 用途：集中管理游戏对象的创建，客户端无需依赖具体游戏类，便于扩展新棋类或替换实现。  

- 模板方法模式（Template Method）  
	- 体现：抽象类 `Game` 提供共性流程与受保护的辅助方法，具体子类实现 `make_move`。  
	- 用途：将不变部分（历史记录、回合切换）放在基类，变更部分（各棋类规则）由子类实现，便于代码复用与规范化。  

- 依赖注入（简单 DI 实践）  
	- 体现：`ConsoleClient` 通过构造函数接收 `GameFactory`，客户端不负责创建具体游戏类。  
	- 用途：提高可测试性与可替换性。  

（注：项目也体现若干 OOP 最佳实践，如单一职责、封装与接口设计）

---

## 7. 分层与“前后端分离”说明

为保持清晰的职责分工，项目采用了简单但严谨的分层：

- 后端（核心，`src/core/`）  
	- 包含棋盘、规则、工厂与序列化逻辑。  
	- 负责业务逻辑和数据表示，保证与 UI 无关。  

- 前端（客户端，`src/client/`）  
	- 目前为命令行客户端 `ConsoleClient`，负责用户交互与展示。  
	- 通过 `Game` / `Board` 的公开接口与后端交互，不直接修改内部数据结构。  

优势：该分层使得将来替换前端（例如 GUI、Web 前端或远程客户端）时无需改动核心逻辑；相同的核心可被多种客户端复用，利于教学演示“前后端分离”的设计思想。

---

## 8. 数据流示例（典型交互）

1. 客户端读取用户命令（例如 `move 3 4`）。  
2. `ConsoleClient` 将命令解析为 `game.make_move(3,4)`。  
3. `GomokuGame.make_move` 或 `GoGame.make_move` 使用 `Board.place_piece` 与基类工具完成落子、历史记录、胜负判定。  
4. 客户端通过 `board.get_piece` 渲染棋盘并显示给用户。  
5. 用户可 `save`，客户端调用 `serialization.save_game` 将 JSON 写入磁盘。  

---

## 9. 异常处理策略与健壮性

- 核心层（`Board`/`Game`/子类）通过明确异常类型（例如 `InvalidPositionError`, `PositionOccupiedError`, `ValueError`）报告非法操作；这些异常包含可读信息，便于客户端提示用户。  
- 客户端捕获常见异常（`ValueError`, `FileNotFoundError`, `IOError` 等），并打印友好提示后继续事件循环，避免程序崩溃。  
- 单元测试覆盖关键路径以确保规则实现的稳定性。  

---

## 10. 可扩展性与教学建议

- 可扩展方向（后续阶段）  
	- 补全围棋高级规则（劫争检测、精确计分、眼的判定）。  
	- 添加 AI（可用最小策略、蒙特卡洛或规则引导）、并展示策略模式/命令模式的使用。  
	- 替换或并行实现 GUI 前端（例如使用 PyQt、Tkinter 或 Web 前端），展示前后端分离的好处。  
	- 支持棋谱保存（如 SGF），并实现历史回放功能。  

- 教学活动建议  
	- 课堂任务：让学生实现新的棋种（如 Reversi），并在 `GameFactory` 中注册。  
	- 代码走查：以 `Game` / `GomokuGame` 为例讲解模板方法模式。  

---

## 11. 非功能性考虑

- 可测试性：模块化单元测试已存在并通过，建议在 CI（如 GitHub Actions）中运行测试。  
- 可维护性：模块边界明确，便于多人协作与分工。  
- 可移植性：纯 Python 实现，跨平台支持良好。  

---

## 12. 总结

本阶段实现了一个结构清晰、面向对象的棋类对战平台原型，采用了工厂模式与模板方法模式，核心（`src/core/`）与客户端（`src/client/`）分层明确，适合作为课堂教学示例与后续扩展的基础。文档适合作为第一阶段的设计说明，后续可根据需求补充 UML 图、时序图或更详细的规则说明。



