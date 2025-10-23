# DO NOT modify or add any import statements
from support import *
from display import WTView

# Name: Siddhant Malik
# Student Number: 49899155
# Favorite Duck: Paul the duck
# -----------------------------------------------------------------------------

# Define your classes and functions here


def main() -> None:
    pass


if __name__ == "__main__":
    main()


# --------------------- TILE CLASSES ---------------------
class Tile:
    """Base class for all tiles in the battlefield."""

    def __init__(self, tile_id: str = TILE_ID, blocking: bool = False):
        self.tile_id = tile_id
        self.blocking = blocking

    def __str__(self) -> str:
        return self.tile_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def is_blocking(self) -> bool:
        return self.blocking


class Floor(Tile):
    """Floor tile — always non-blocking."""

    def __init__(self):
        super().__init__(FLOOR_ID, False)


class Wall(Tile):
    """Wall tile — always blocking."""

    def __init__(self):
        super().__init__(WALL_ID, True)


class Rock(Tile):
    """Rock tile — can be destroyed to become non-blocking."""

    def __init__(self, is_destroyed: bool):
        super().__init__(tile_id=ROCK_ID, blocking=not is_destroyed)
        self._destroyed = is_destroyed
        if self._destroyed:
            self.tile_id = DESTROYED_ID
            self.blocking = False

    def __repr__(self) -> str:
        return f"Rock({self._destroyed})"

    def is_destroyed(self) -> bool:
        return self._destroyed

    def destroy(self):
        self._destroyed = True
        self.tile_id = DESTROYED_ID
        self.blocking = False


# --------------------- TANK CLASSES ---------------------
class Tank:
    """Base class for all tanks (player or enemies)."""

    TANK_ID = TANK_ID  # default identifier

    def __init__(self, position: Position, heading: Heading, speed: int):
        self._position = position
        self._heading = heading
        self._speed = speed

    def __repr__(self) -> str:
        return f"Tank({self._position}, {self._heading}, {self._speed})"

    def __str__(self) -> str:
        row, col = self._position
        h_row, h_col = self._heading
        return f"{self.get_id()},{row},{col},{h_row},{h_col},{self._speed}"

    # ---- Getters / Setters ----
    def get_id(self) -> str:
        return self.TANK_ID

    def get_position(self) -> Position:
        return self._position

    def set_position(self, new_pos: Position):
        self._position = new_pos

    def get_heading(self) -> Heading:
        return self._heading

    def set_heading(self, new_heading: Heading):
        self._heading = new_heading

    def get_speed(self) -> int:
        return self._speed

    def set_speed(self, new_speed: int):
        self._speed = new_speed

    # ---- Rotation ----
    def turn_left(self):
        row, col = self._heading
        self._heading = (-col, row)

    def turn_right(self):
        row, col = self._heading
        self._heading = (col, -row)

    def get_symbol(self) -> str:
        """Return string like [P>], [G<], [L^] based on heading."""
        heading_map = {
            (0, 1): '>',
            (0, -1): '<',
            (-1, 0): '^',
            (1, 0): 'v',
        }
        char = heading_map.get(self._heading, '?')
        return f"[{self.TANK_ID}{char}]"


class Player(Tank):
    """The Player tank."""

    TANK_ID = PLAYER_ID

    def __init__(self, position: Position, heading: Heading, speed: int, armour: int):
        super().__init__(position, heading, speed)
        self._armour = armour

    def __repr__(self) -> str:
        return f"Player({self._position}, {self._heading}, {self._speed}, {self._armour})"

    def __str__(self) -> str:
        row, col = self._position
        h_row, h_col = self._heading
        return f"{self.get_id()},{row},{col},{h_row},{h_col},{self._speed},{self._armour}"

    # ---- Armour Management ----
    def get_armour(self) -> int:
        return self._armour

    def set_armour(self, new_armour: int):
        self._armour = new_armour

    def is_destroyed(self) -> bool:
        return self._armour <= 0

    def take_damage(self, amount: int = 1):
        """Reduce armour by amount."""
        self._armour = max(0, self._armour - amount)

    # ---- Heading Utilities ----
    def reverse_heading(self):
        dx, dy = self._heading
        self._heading = (-dx, -dy)


class Enemy(Tank):
    """Base class for all enemies."""

    TANK_ID = ENEMY_ID

    def __repr__(self) -> str:
        return f"Enemy({self._position}, {self._heading}, {self._speed})"

    def take_action(self, visible_tiles: list[Tile]):
        """Default: enemies do nothing."""
        pass

    def apply_effect(self, target: Tank):
        """Default: enemies do nothing."""
        pass


class Guard(Enemy):
    TANK_ID = GUARD_ID

    def __init__(self, position: Position, heading: Heading, speed: int):
        super().__init__(position, heading, speed)

    def __repr__(self) -> str:
        # Ensure correct class name
        return f"Guard({self._position}, {self._heading}, {self._speed})"

    def take_action(self, visible_tiles: list[Tile]):
        self.turn_left()

    def apply_effect(self, target: Tank):
        target.set_speed(-2)


class Patrol(Enemy):
    TANK_ID = PATROL_ID
    DESIRED_SPEED = 2

    def __init__(self, position: Position, heading: Heading, speed: int):
        super().__init__(position, heading, speed)

    def __repr__(self) -> str:
        return f"Patrol({self._position}, {self._heading}, {self._speed})"

    def take_action(self, visible_tiles: list[Tile]):
        if len(visible_tiles) > 2:
            # Enough space: move forward
            self.set_speed(self.DESIRED_SPEED)
        else:
            # Not enough space: reverse heading
            row, col = self.get_heading()
            self.set_heading((-row, -col))
            self.set_speed(self.DESIRED_SPEED)

    def apply_effect(self, target: Tank):
        # Reverse target heading vector
        row, col = target.get_heading()
        target.set_heading((-row, -col))



# --------------------- BATTLEFIELD ---------------------
class Battlefield:
    """Represents the battlefield grid."""

    def __init__(self, tiles: list[list[Tile]]):
        self._tiles = tiles
        self._rows = len(tiles)
        self._cols = len(tiles[0]) if tiles else 0

    def __repr__(self) -> str:
        return f"Battlefield({self._tiles})"

    def __str__(self) -> str:
        return "\n".join("".join(str(tile) for tile in row) for row in self._tiles)

    def get_tiles(self) -> list[list[Tile]]:
        return self._tiles

    def get_tile(self, pos: Position) -> Tile:
        x, y = pos
        return self._tiles[x][y]

    def get_rocks(self) -> dict[Position, Rock]:
        rocks = {}
        for r, row in enumerate(self._tiles):
            for c, tile in enumerate(row):
                if isinstance(tile, Rock):
                    rocks[(r, c)] = tile
        return rocks

    def in_bounds(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self._rows and 0 <= y < self._cols


# --------------------- WTModel ---------------------
class WTModel:
    """Logical game state for We Tank!"""

    def __init__(self, battlefield: Battlefield, player: Player, enemies: list[Enemy]):
        self._battlefield = battlefield
        self._player = player
        self._enemies = enemies.copy()

    def __repr__(self) -> str:
        return f"WTModel({repr(self._battlefield)}, {repr(self._player)}, {repr(self._enemies)})"

    def __str__(self) -> str:
        battlefield_str = str(self._battlefield)
        player_str = str(self._player)
        enemies_str = "\n".join(str(e) for e in self._enemies)
        return f"{battlefield_str}\n\n{player_str}\n{enemies_str}" if enemies_str else f"{battlefield_str}\n\n{player_str}"

    def get_battlefield(self) -> Battlefield:
        return self._battlefield

    def get_player(self) -> Player:
        return self._player

    def get_enemies(self) -> list[Enemy]:
        return self._enemies

    def has_won(self) -> bool:
        return len(self._enemies) == 0 and self._player.get_armour() > 0

    def has_lost(self) -> bool:
        return self._player.get_armour() <= 0

    def tank_positions(self) -> dict[Position, Tank]:
        positions = {self._player.get_position(): self._player}
        for enemy in self._enemies:
            positions[enemy.get_position()] = enemy
        return positions

    def visible_positions(self, tank: Tank) -> list[Position]:
        positions = []
        x, y = tank.get_position()
        dx, dy = tank.get_heading()
        battlefield = self._battlefield

        while True:
            x += dx
            y += dy
            if not battlefield.in_bounds((x, y)):
                break
            positions.append((x, y))
            tile = battlefield.get_tile((x, y))
            if tile.is_blocking():
                break
        return positions

    # --- Movement & combat ---
    def advance_tank(self, tank: Tank):
        speed = tank.get_speed()
        if speed == 0:
            return

        dx, dy = tank.get_heading()
        steps = speed
        if speed < 0:
            dx, dy = -dx, -dy
            steps = -speed

        occupied = self.tank_positions()
        occupied.pop(tank.get_position(), None)

        x, y = tank.get_position()
        for _ in range(steps):
            nx, ny = x + dx, y + dy
            if not self._battlefield.in_bounds((nx, ny)):
                break
            tile = self._battlefield.get_tile((nx, ny))
            if tile.is_blocking() or (nx, ny) in occupied:
                break
            x, y = nx, ny

        tank.set_position((x, y))
        tank.set_speed(0)

    def get_attack_target(self, tank: Tank) -> Position:
        occupied = self.tank_positions()
        for pos in self.visible_positions(tank):
            other = occupied.get(pos)
            if other is not None and other is not tank:
                return pos
            tile = self._battlefield.get_tile(pos)
            if tile.is_blocking():
                return pos
        return None

    def enemy_actions(self):
        player_hit = False
        player_pos = self._player.get_position()

        for enemy in list(self._enemies):
            visible_tiles = self.visible_positions(enemy)
            target = self.get_attack_target(enemy)

            if player_pos in visible_tiles and target == player_pos and not player_hit:
                self._player.take_damage(1)
                player_hit = True
                if isinstance(enemy, Guard):
                    self._player.set_speed(-2)
                elif isinstance(enemy, Patrol):
                    self._player.turn_left()
                    self._player.turn_left()
            else:
                if isinstance(enemy, Guard):
                    enemy.turn_left()
                elif isinstance(enemy, Patrol):
                    if len(visible_tiles) >= 2:
                        enemy.set_speed(2)
                    else:
                        enemy.turn_left()
                        enemy.turn_left()

            self.advance_tank(enemy)

    def player_fire(self):
        target = self.get_attack_target(self._player)
        if target is None:
            return
        for enemy in self._enemies:
            if enemy.get_position() == target:
                self._enemies.remove(enemy)
                return
        tile = self._battlefield.get_tile(target)
        if hasattr(tile, "destroy"):
            tile.destroy()

    def player_move(self, move: str):
        if move == "left":
            self._player.turn_left()
        elif move == "right":
            self._player.turn_right()
        elif move == "forward":
            self._player.set_speed(1)
            self.advance_tank(self._player)
        elif move == "back":
            self._player.set_speed(1)
            self._player.reverse_heading()
            self.advance_tank(self._player)
            self._player.reverse_heading()
        self._player.set_speed(0)

    def is_game_over(self) -> bool:
        return self.has_won() or self.has_lost()


    # --------------------- File I/O ---------------------
def load_model(file: str) -> WTModel:
    """
    Load a WTModel instance from the specified file.

    The file must follow the string representation format of a WTModel.
    Raises:
        ValueError: if the file contains invalid tiles, player, or enemy data.
        FileNotFoundError: if the file does not exist (not caught here).
    """
    # Read file contents (no file-not-found handling per spec)
    with open(file, "r", encoding="utf-8") as fh:
        content = fh.read().rstrip("\n")

    # Split battlefield and entities
    parts = content.split("\n\n", 1)
    if len(parts) != 2:
        raise ValueError(INVALID_TILE_MSG)

    battlefield_block, entities_block = parts
    battlefield_rows = [line.rstrip("\n") for line in battlefield_block.splitlines()]

    # --- Build battlefield ---
    tiles: list[list[Tile]] = []
    for row in battlefield_rows:
        row_tiles: list[Tile] = []
        for ch in row:
            if ch == "W":
                row_tiles.append(Wall())
            elif ch == " ":
                row_tiles.append(Floor())
            elif ch == "R":
                row_tiles.append(Rock(False))
            elif ch == "X":
                row_tiles.append(Rock(True))
            else:
                raise ValueError(INVALID_TILE_MSG)
        tiles.append(row_tiles)

    battlefield = Battlefield(tiles)

    # --- Parse entities ---
    entity_lines = [ln.strip() for ln in entities_block.splitlines() if ln.strip()]
    if not entity_lines:
        raise ValueError(INVALID_PLAYER_MSG)

    # Player line
    player_line = entity_lines[0]
    parts = [p.strip() for p in player_line.split(",")]
    if len(parts) < 7 or parts[0] != Player.TANK_ID:
        raise ValueError(INVALID_PLAYER_MSG)

    try:
        prow, pcol = int(parts[1]), int(parts[2])
        phr, phc = int(parts[3]), int(parts[4])
        pspeed = int(parts[5])
        parmour = int(parts[6])
        player = Player((prow, pcol), (phr, phc), pspeed, parmour)
    except Exception:
        raise ValueError(INVALID_PLAYER_MSG)

    # Enemy lines
    enemies: list[Enemy] = []
    for line in entity_lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            raise ValueError(INVALID_ENEMY_MSG)
        eid = parts[0]
        try:
            erow, ecol = int(parts[1]), int(parts[2])
            ehr, ehc = int(parts[3]), int(parts[4])
            espeed = int(parts[5])
        except Exception:
            raise ValueError(INVALID_ENEMY_MSG)

        if eid == Guard.TANK_ID:
            enemies.append(Guard((erow, ecol), (ehr, ehc), espeed))
        elif eid == Patrol.TANK_ID:
            enemies.append(Patrol((erow, ecol), (ehr, ehc), espeed))
        else:
            raise ValueError(INVALID_ENEMY_MSG)

    # Return fully constructed model
    return WTModel(battlefield, player, enemies)



# --------------------- CONTROLLER ---------------------
class WTController:
    """Controller for We Tank! game loop."""

    def __init__(self, initial_state: WTModel):
        self._model = initial_state
        self._view = WTView()

    def __repr__(self) -> str:
        return f"WTController({repr(self._model)})"

    def __str__(self) -> str:
        return str(self._model)

    def print_game(self):
        self._view.draw_game(
            self._model.get_battlefield().get_tiles(),
            self._model.get_player(),
            self._model.get_enemies(),
        )

    def load_game(self, file: str):
        """
        Replace the current game state with the state contained in the given file.
        Raises:
            ValueError: if the file cannot be found or the contents are invalid.
        """
        try:
            # Try to load using load_model
            self._model = load_model(file)
            print(LOAD_MSG)

        except FileNotFoundError:
            # Convert file-not-found to a ValueError with correct message
            raise ValueError(FILE_NOT_FOUND_MSG)

        except ValueError as e:
            # Reraise any ValueError (invalid tiles, player, or enemy data)
            raise
    
    def save_game(self, file: str) -> None:
        """
        Save the current WTModel state to a file.

        Args:
            file (str): The file path to save the model into.
        """
        with open(file, "w", encoding="utf-8") as fh:
            fh.write(str(self._model))
        print(SAVE_MSG)

    def get_command(self) -> str:
        valid_commands = [
            MOVE + " " + FORWARD,
            MOVE + " " + BACK,
            TURN + " " + LEFT,
            TURN + " " + RIGHT,
            FIRE,
            WAIT,
            HELP,
            QUIT,
        ]
        while True:
            command = input(COMMAND_PROMPT)
            lower_cmd = command.lower()
            if lower_cmd.startswith(SAVE + " ") or lower_cmd.startswith(LOAD + " "):
                return lower_cmd
            if lower_cmd in valid_commands:
                return lower_cmd
            print(INVALID_COMMAND_MSG)

    def play(self):
        self.print_game()
        print(WELCOME_MSG)
        while not self._model.is_game_over():
            cmd = self.get_command()
            if cmd == QUIT:
                return
            elif cmd == HELP:
                print(HELP_MSG)
                continue
            elif cmd == MOVE + " " + FORWARD:
                self._model.player_move("forward")
            elif cmd == MOVE + " " + BACK:
                self._model.player_move("back")
            elif cmd == TURN + " " + LEFT:
                self._model.player_move("left")
            elif cmd == TURN + " " + RIGHT:
                self._model.player_move("right")
            elif cmd == FIRE:
                self._model.player_fire()
            elif cmd == WAIT:
                pass
            elif cmd.startswith(SAVE + " "):
                filename = cmd.split(maxsplit=1)[1]
                self.save_game(filename)
                continue
            elif cmd.startswith(LOAD + " "):
                filename = cmd.split(maxsplit=1)[1]
                try:
                    self.load_game(filename)
                    self.print_game()
                except ValueError as e:
                    # Catch and print the error message (e.g., "Cannot locate the desired file!")
                    print(e)
                continue

            # Enemy actions after player's turn
            if not self._model.is_game_over():
                self._model.enemy_actions()
                self.print_game()

        # Game over messages
        if self._model.has_won():
            self.print_game()
            print(WIN_MSG)
        else:
            print(LOSE_MSG)


# --------------------- HELPER FUNCTION ---------------------
def play_game(file: str):
    """
    Load a WTModel from file, create a controller, and play the game.
    """
    model = load_model(file)
    controller = WTController(model)
    controller.play()
