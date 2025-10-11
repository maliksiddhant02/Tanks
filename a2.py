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
        super().__init__(FLOOR_ID, False)  # call parent constructor


class Wall(Tile):
    def __init__(self):
        super().__init__(WALL_ID, True)  # call parent constructor