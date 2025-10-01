Position = tuple[int,int]
Heading = Position

TILE_ID = "T"
FLOOR_ID = " "
WALL_ID = "W"
ROCK_ID = "R"
DESTROYED_ID = "X"

TANK_ID = "K"
PLAYER_ID = "P"
ENEMY_ID = "E"
GUARD_ID = "G"
PATROL_ID = "L"

TURN = "turn"
LEFT = "left"
RIGHT = "right"
MOVE = "move"
FORWARD = "forward"
BACK = "back"
WAIT = "wait"
FIRE = "fire"

HELP = "help"
QUIT = "quit"
SAVE = "save"
LOAD = "load"

WELCOME_MSG = "Its time to tank!"
COMMAND_PROMPT = "Please enter a command (help for list of valid commands): "
INVALID_COMMAND_MSG = "Invalid Command! Type `help` for a list of commands"

SAVE_MSG = "Game successfully saved!"
LOAD_MSG = "Game successfully loaded!"
HELP_MSG = """Commands: 
 - `move [forward|back]`: Move tank in specified direction.
 - `turn [left|right]`: Turn tank 90 degrees in specified direction.
 - `wait`: Do nothing this turn.
 - `fire`: Fire!
 - `save F`: Save game to F
 - `load F`: Load game from F
 - `help`: Print this help message.
 - `quit`: Exit Game."""

WIN_MSG = "Congratulations! You destroyed all enemy tanks!"
LOSE_MSG = "You have been destroyed..."

FILE_NOT_FOUND_MSG = "Cannot locate the desired file!"
INVALID_TILE_MSG = "Invalid Tile!"
INVALID_PLAYER_MSG = "Invalid Player Values!"
INVALID_ENEMY_MSG = "Invalid Enemy Values!"