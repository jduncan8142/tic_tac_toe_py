from typing import Optional
import pyray as pr
from enum import Enum
from time import sleep


class EntityType(Enum):
    X = 1
    O = 2
    U = 3  # Undefined
    C = 4  # Cat
    A = 5  # AI (if needed)


class Position:
    def __init__(self, row: int = 0, col: int = 0) -> None:
        self.row: int = row
        self.col: int = col


class Entity:
    def __init__(self, entity_type: EntityType, position: Position) -> None:
        self.type: EntityType = entity_type
        self.position: Position = position


class Board:
    def __init__(self) -> None:
        self.grid: list[list[Entity]] = [[Entity(EntityType.U, Position(r, c)) for c in range(3)] for r in range(3)]

    def reset(self) -> None:
        self.grid = [[Entity(EntityType.U, Position(r, c)) for c in range(3)] for r in range(3)]

    def new_game(self) -> None:
        self.reset()


class Player:
    def __init__(self, player_type: EntityType, player_name: Optional[str | None] = None) -> None:
        self.type = player_type
        self.player_name: str | None = player_name
        self.score: int = 0
        self.is_winner: bool = False
        self.ai: bool = False  # Indicates if the player is an AI

    def reset(self) -> None:
        self.is_winner = False
        self.score = 0

    def new_game(self) -> None:
        self.is_winner = False


class Cat:
    def __init__(self) -> None:
        self.type: EntityType = EntityType.C
        self.score: int = 0
        self.is_winner: bool = False

    def reset(self) -> None:
        self.score = 0
        self.is_winner = False


class Game:
    def __init__(self, screenWidth, screenHeight) -> None:
        self.screenWidth: int = screenWidth
        self.screenHeight: int = screenHeight
        self.board = Board()
        self.player1: Player = Player(player_type=EntityType.X)
        self.player2: Player = Player(player_type=EntityType.O)
        self.cat: Cat = Cat()
        self.number_of_players: int | None = None
        self.current_player: Player | None = None
        self.games_played: int = 0
        self.game_started: bool = False
        self.game_finished: bool = False
        self.line_width: int = 5
        self.cell_width: int = 100
        self.cell_height: int = 100

    def startup(self) -> None:
        pr.init_audio_device()
        self.reset()

    def win_check(self) -> bool:
        # Check rows, columns, and diagonals for a player win
        for i in range(3):
            if (
                self.board.grid[i][0].type == self.board.grid[i][1].type == self.board.grid[i][2].type != EntityType.U
            ) or (
                self.board.grid[0][i].type == self.board.grid[1][i].type == self.board.grid[2][i].type != EntityType.U
            ):
                return True
        if (self.board.grid[0][0].type == self.board.grid[1][1].type == self.board.grid[2][2].type != EntityType.U) or (
            self.board.grid[0][2].type == self.board.grid[1][1].type == self.board.grid[2][0].type != EntityType.U
        ):
            return True
        # Check for a draw
        if all(cell.type != EntityType.U for row in self.board.grid for cell in row):
            self.cat.is_winner = True
            self.cat.score += 1
            self.game_finished = True
            return True
        return False

    def handle_mouse_click(self) -> None:
        if self.current_player is not None:
            mouse_pos = pr.get_mouse_position()
            # Game is in progress
            if self.game_started and not self.game_finished:
                col = int(mouse_pos.x // (self.screenWidth // 3))
                row = int(mouse_pos.y // (self.screenHeight // 3))
                if 0 <= row < 3 and 0 <= col < 3:
                    cell = self.board.grid[row][col]
                    if cell.type == EntityType.U:
                        cell.type = self.current_player.type
                        # cell.position = Position(row, col)
                        if self.win_check():
                            self.current_player.is_winner = True
                            self.current_player.score += 1
                            self.game_finished = True
                        else:
                            self.set_current_player()

    def handle_number_of_players(self) -> None:
        if self.number_of_players == 0:
            self.player1.ai = True
            self.player2.ai = True
            self.current_player = self.player1
        if self.number_of_players == 1:
            self.player1.ai = False
            self.player2.ai = True
        elif self.number_of_players == 2:
            self.player1.ai = False
            self.player2.ai = False

    def ai_move(self) -> None:
        for player in [self.player1, self.player2]:
            if player.ai:
                sleep(1)  # Simulate thinking time for AI
                # Implement AI logic here
                # For simplicity, we can just make a random valid move
                available_moves = [
                    (r, c) for r in range(3) for c in range(3) if self.board.grid[r][c].type == EntityType.U
                ]
                if available_moves:
                    row, col = available_moves[0]
                    self.board.grid[row][col].type = player.type

    def update(self) -> None:
        if self.player1.ai or self.player2.ai:
            self.ai_move()
        if pr.is_key_pressed(pr.KeyboardKey.KEY_S) or pr.is_key_pressed(pr.KeyboardKey.KEY_N):
            self.new_game()
        if pr.is_key_pressed(pr.KeyboardKey.KEY_R):
            self.reset()
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            self.shutdown()
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ONE):
            self.number_of_players = 1
        if pr.is_key_pressed(pr.KeyboardKey.KEY_TWO):
            self.number_of_players = 2
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ZERO):
            self.number_of_players = 0
        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
            self.handle_mouse_click()

    def render(self) -> None:
        # Render game elements here
        if self.game_started and not self.game_finished:
            # Game is in progress
            for row in range(3):
                for col in range(3):
                    pr.draw_rectangle(
                        (col * self.cell_width) + (self.line_width * (col + 1)),
                        (row * self.cell_height) + (self.line_width * (row + 1)),
                        self.cell_width - 10,
                        self.cell_height - 10,
                        pr.GRAY,
                    )
                    cell = self.board.grid[row][col]
                    if cell.type == EntityType.X:
                        pr.draw_text("X", col * self.cell_width + 40, row * self.cell_height + 30, 50, pr.RED)
                    elif cell.type == EntityType.O:
                        pr.draw_text("O", col * self.cell_width + 40, row * self.cell_height + 30, 50, pr.BLUE)
        elif self.game_started and self.game_finished:
            # Game has finished
            pr.draw_rectangle(
                self.line_width,
                self.line_width,
                self.screenWidth - (self.line_width * 2),
                self.screenHeight - (self.line_width * 2),
                pr.GRAY,
            )  # Draw the game overlay
            for index, player in enumerate([self.player1, self.player2, self.cat]):
                _player_name: str = ""
                if player.type == EntityType.C:
                    _player_name = "Cat"
                else:
                    if player.type == EntityType.X:
                        _player_name = self.player1.player_name if self.player1.player_name else "Player 1"
                    elif player.type == EntityType.O:
                        _player_name = self.player2.player_name if self.player2.player_name else "Player 2"
                pr.draw_text(
                    f"{_player_name} Score: {player.score}",
                    10,
                    50 + (index * 30),
                    20,
                    pr.WHITE,
                )
                if player.is_winner:
                    pr.draw_text("WINNER!", 210, 50 + (index * 30), 20, pr.GREEN)
        elif not self.game_started and not self.game_finished:
            # Game is not started
            pr.draw_rectangle(
                self.line_width,
                self.line_width,
                self.screenWidth - (self.line_width * 2),
                self.screenHeight - (self.line_width * 2),
                pr.GRAY,
            )
            if self.number_of_players is None:
                pr.draw_text("Number of players?", 10, 10, 20, pr.WHITE)
            else:
                pr.draw_text(f"Number of players: {self.number_of_players}", 10, 10, 20, pr.WHITE)
            pr.draw_text("(S)tart the Game", 10, 40, 20, pr.WHITE)
            pr.draw_text("(R)eset the Game", 10, 70, 20, pr.WHITE)
            pr.draw_text("(N)ew Game", 10, 100, 20, pr.WHITE)
            pr.draw_text("'ESC' to Exit", 10, 130, 20, pr.WHITE)

    def shutdown(self) -> None:
        pr.close_audio_device()
        pr.close_window()
        exit(0)

    def reset(self) -> None:
        self.number_of_players = None
        self.board.reset()
        self.player1.reset()
        self.player2.reset()
        self.cat.reset()
        self.current_player = None
        self.game_started = False
        self.game_finished = False

    def set_current_player(self) -> None:
        match self.current_player:
            case self.player1:
                self.current_player = self.player2
            case self.player2:
                self.current_player = self.player1
            case _:
                self.current_player = self.player1

    def new_game(self) -> None:
        self.games_played += 1
        self.game_started = True
        self.game_finished = False
        self.board.reset()
        self.player1.new_game()
        self.player2.new_game()
        self.set_current_player()
