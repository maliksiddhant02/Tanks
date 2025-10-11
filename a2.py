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

class Tile:
    def __init__(self, tile_id=TILE_ID, blocking=False):
        self.tile_id = tile_id
        self.blocking = blocking

    def __str__(self) -> str:
        return self.tile_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def is_blocking(self) -> bool:
        return self.blocking

class Floor(Tile):
    def __init__(self):
        super().__init__(FLOOR_ID, False)

class Wall(Tile):
    def __init__(self):
        super().__init__(WALL_ID, True)

class Rock(Tile):
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

class Player(Tank):
    TANK_ID = PLAYER_ID  # Player symbol

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
    
    # ---- Heading Utilities ----
    def reverse_heading(self):
        """Reverse the current heading of the player."""
        dx, dy = self._heading
        self._heading = (-dx, -dy)
    
class Enemy(Tank):
    TANK_ID = ENEMY_ID

    def __init__(self, position: Position, heading: Heading, speed: int):
        super().__init__(position, heading, speed)

    def __repr__(self) -> str:
        return f"Enemy({self._position}, {self._heading}, {self._speed})"

    def __str__(self) -> str:
        row, col = self._position
        h_row, h_col = self._heading
        return f"{self.get_id()},{row},{col},{h_row},{h_col},{self._speed}"

    # ---- Enemy-specific actions ----
    def take_action(self, visible_tiles: list[Tile]):
        # Abstract enemies do nothing by default
        pass

    def apply_effect(self, target: Tank):
        # Abstract enemies do nothing by default
        pass

class Guard(Enemy):
    TANK_ID = GUARD_ID

    def __init__(self, position: Position, heading: Heading, speed: int):
        super().__init__(position, heading, speed)

    def __repr__(self) -> str:
        return f"Guard({self._position}, {self._heading}, {self._speed})"

    def take_action(self, visible_tiles: list[Tile]):
        # Guard always turns left
        self.turn_left()

    def apply_effect(self, target: Tank):
        # Set target speed to -2
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
            self.set_speed(self.DESIRED_SPEED)
        else:
            # Rotate 180°: two left turns
            self.turn_left()
            self.turn_left()

    def apply_effect(self, target: Tank):
        # Rotate target 180°
        target.turn_left()
        target.turn_left()

class Battlefield:
    def __init__(self, tiles: list[list["Tile"]]):
        self._tiles = tiles
        self._rows = len(tiles)
        self._cols = len(tiles[0]) if tiles else 0  # handle empty battlefield

    def __repr__(self) -> str:
        return f"Battlefield({self._tiles})"

    def __str__(self) -> str:
        return "\n".join("".join(str(tile) for tile in row) for row in self._tiles)

    def get_tiles(self) -> list[list["Tile"]]:
        return self._tiles

    def get_tile(self, pos: "Position") -> "Tile":
        """Return the tile at the given (x, y) position."""
        x, y = pos
        return self._tiles[x][y]

    def get_rocks(self) -> dict["Position", "Rock"]:
        rocks = {}
        for r, row in enumerate(self._tiles):
            for c, tile in enumerate(row):
                if isinstance(tile, Rock):
                    rocks[(r, c)] = tile
        return rocks

    def in_bounds(self, pos: "Position") -> bool:
        x, y = pos
        return 0 <= x < self._rows and 0 <= y < self._cols

    
    
class WTModel:
    """
    WTModel models the logical state of a game of We Tank!.
    """

    def __init__(self, battlefield: "Battlefield", player: "Player", enemies: list["Enemy"]):
        """
        Initialise a new WTModel instance with battlefield, player, and enemies.
        Enemies are stored in priority order: first is highest priority.
        """
        self._battlefield = battlefield
        self._player = player
        self._enemies = enemies.copy()

    def __repr__(self) -> str:
        """
        Return a string that can recreate this WTModel instance in a REPL.
        """
        return f"WTModel({repr(self._battlefield)}, {repr(self._player)}, {repr(self._enemies)})"

    def __str__(self) -> str:
        """
        Return a string representation of the battlefield, player, and enemies.
        Battlefield first, followed by two newlines, then player, newline, then enemies.
        """
        battlefield_str = str(self._battlefield)
        player_str = str(self._player)
        enemies_str = "\n".join(str(enemy) for enemy in self._enemies)
        return f"{battlefield_str}\n\n{player_str}\n{enemies_str}" if enemies_str else f"{battlefield_str}\n\n{player_str}"

    def get_battlefield(self) -> "Battlefield":
        """Return this model's battlefield instance."""
        return self._battlefield

    def get_player(self) -> "Player":
        """Return this model's player instance."""
        return self._player

    def get_enemies(self) -> list["Enemy"]:
        """Return the list of enemies in decreasing priority order."""
        return self._enemies

    def has_won(self) -> bool:
        """Return True if all enemies are destroyed."""
        return len(self._enemies) == 0 and self._player.get_armour() > 0

    def has_lost(self) -> bool:
        """Return True if the player has no armour left."""
        return self._player.get_armour() <= 0

    def tank_positions(self) -> dict["Position", "Tank"]:
        """
        Return a dictionary mapping positions to tanks.
        Includes player and all enemies.
        """
        positions = {self._player.get_position(): self._player}
        for enemy in self._enemies:
            positions[enemy.get_position()] = enemy
        return positions

    def visible_positions(self, tank: "Tank") -> list["Position"]:
        """
        Return a list of positions visible to the tank, in order of distance.
        Stops at blocking tile. Includes positions with other tanks.
        Excludes the tank's own position.
        """
        positions = []
        x, y = tank.get_position()
        dx, dy = tank.get_heading()
        battlefield = self._battlefield

        while True:
            x += dx
            y += dy

            if not battlefield.in_bounds((x, y)):
                break

            positions.append((x, y))  # include this position

            tile = battlefield.get_tile((x, y))

            # stop if tile blocks visibility
            if tile.is_blocking():
                break

            # do NOT break on other tanks; they are visible but do not block vision

        return positions

    
    def advance_tank(self, tank: "Tank"):
        """
            Move the tank according to its heading and speed.
            Stop if another tank or blocking tile encountered.
            Reset tank speed to 0 after movement.
        """
    
        speed = tank.get_speed()
        x, y = tank.get_position()
        dx, dy = tank.get_heading()
        
        for _ in range(speed):
            nx, ny = x + dx, y + dy
            # blocked by battlefield bounds
            if not self._battlefield.in_bounds((nx, ny)):
                break
            # blocked by tile
            tile = self._battlefield.get_tile((nx, ny))
            if tile.is_blocking():
                break
            # blocked by another tank
            if (nx, ny) in self.tank_positions():
                break
            # move
            x, y = nx, ny
        tank.set_position((x, y))
        tank.set_speed(0)
    
    def get_attack_target(self, tank: "Tank") -> "Position":
        """
        Return the first tile or tank that would be hit if tank fires.
        Must be in the tank's visible positions.
        """
        for pos in self.visible_positions(tank):
            if pos in self.tank_positions() and self.tank_positions()[pos] != tank:
                return pos
            tile = self._battlefield.get_tile(pos)
            if tile.is_blocking():
                return pos
        return None


    def enemy_actions(self):
        """
        Process each enemy's action in priority order.
        Fire if player is visible; otherwise call enemy.take_action(visible_tiles).
        Apply advance_tank after action. Reduce player armour if hit and reverse
        player's heading (180 degrees).
        """
        for enemy in self._enemies:
            visible_tiles = self.visible_positions(enemy)
    
            # If player is in enemy's line-of-fire, enemy "fires" (even if a blocking tile
            # is hit first). If the attack target is the player, reduce armour and reverse heading.
            if self._player.get_position() in visible_tiles:
                target = self.get_attack_target(enemy)
                if target == self._player.get_position():
                    # player got hit: reduce armour (not below 0)
                    self._player.set_armour(max(0, self._player.get_armour() - 1))
    
                    # reverse player's heading 180 degrees
                    hx, hy = self._player.get_heading()
                    self._player.set_heading((-hx, -hy))
            else:
                # Player not visible → enemy performs its AI action.
                enemy.take_action(visible_tiles)
    
            # After the action (or firing), the enemy advances according to its speed.
            self.advance_tank(enemy)


    def player_fire(self):
        """
        Resolve the player firing.
        Hits the closest visible enemy or blocking tile.
        Update battlefield and enemies accordingly.
        """
        target = self.get_attack_target(self._player)
        if target is None:
            return
        # check for enemy hit
        for enemy in self._enemies:
            if enemy.get_position() == target:
                self._enemies.remove(enemy)
                return
        # check for tile hit
        tile = self._battlefield.get_tile(target)
        if hasattr(tile, "destroy"):
            tile.destroy()

    def player_move(self, move: str):
        """
        Move or turn the player according to the move command:
        'left', 'right', 'forward', or 'back'.
        Movement speed is 1, reset speed to 0 after.
        """
        if move == 'left':
            self._player.turn_left()
        elif move == 'right':
            self._player.turn_right()
        elif move == 'forward':
            self._player.set_speed(1)
            self.advance_tank(self._player)
        elif move == 'back':
            self._player.set_speed(1)
            self._player.reverse_heading()
            self.advance_tank(self._player)
            self._player.reverse_heading()
        self._player.set_speed(0)
