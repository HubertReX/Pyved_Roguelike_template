GAME_VER = "0.9"
# print exceptions in GUI only in debug mode (useful for debugging highscore local web storage when there is no terminal)
IS_DEBUG = True # check if we can use __debug__ with pyved and pygbag

show_input = False
user_name_input = None 
user_name = None 

fonts = {}
# Need a flag to handle differently when game is run in desktop mode or in a web browser
IS_WEB = False
# local storage in web version for high score table
if __import__("sys").platform == "emscripten":
    IS_WEB = True
    
### Highscore utils
# there are 3 implementations of highscore:
# 1. using GameJolt API for desktop mode
#    * unfortunately it doesn't work yet when run in the web browser
#    * API does the all heavy lifting
#    * scores are kept online and there is one common score board for all users no matter when the game is run
# 2. Local storage in web browser
#    * uses the build in Web browser functionality called 'local storage'
#    * highscore table is kept in your browser locally and bind to url (domain:port, eg.: pyvm.kata.games, localhost:8000, 127.0.0.1:8000) so it's decentralized
#    * it can be viewed and edited in browser (e.g. in Chrome: Developer Tools -> Applications -> Storage -> Local storage -> url)
# 3. Local storage stub
#    * stubs local storage to make it easier to debug
#    * when enabled, you can run game in desktop mode and still test it (view console, quick restart, etc.)
#    * the data is kept in global dictionary (HIGHSCORE_STUB) instead of actual browser local storage
#    * it's restored to original state with each game run

# Local storage stub for testing highscore in desktop mode
USE_HIGHSCORE_STUB = False
HIGHSCORE_STUB = {
    # "Ula": {"level": 3, "stored_timestamp": "1712989042.312", "game_ver": "0.9", "time_played": "n/a"},
    # "Hubi": {"level": 2, "stored_timestamp": "1712988963.14", "game_ver": "0.9", "time_played": "n/a"},
    # "Master": {"level": 4, "stored_timestamp": "1712989177.01", "game_ver": "0.9", "time_played": "n/a"},
    # "Noob": {"level": 2, "stored_timestamp": "1712989177.01", "game_ver": "0.9", "time_played": "n/a"},
    # "Ela": {"level": 1, "stored_timestamp": "1712989127.556", "game_ver": "0.9", "time_played": "n/a"},
    # "Ala": {"level": 1, "stored_timestamp": "1712988973.809", "game_ver": "0.9", "time_played": "n/a"},
}
if USE_HIGHSCORE_STUB:
    IS_WEB = True

# GameJolt API
# go to https://gamejolt.com/
# create account
# crate new game
GAME_ID = "" # <YOUR_GAME_ID>
PRIVATE_KEY = "" # <YOUR_KEY>
gamejoltapi = None
TEST_SCORE_TABLE_ID = 0 # create test score table and enter it's id here
PROD_SCORE_TABLE_ID = 0 # open default score table and enter it's id here
SCORE_TABLE = []
SCORES = {}
NO_TOP_SCORES = 10

screen = None
is_game_over = False
status_label = None

game_over_msgs_hs = [
    "Game Over",
    'You reached level : {level_count}',
    'Provide your name for highscore table',
    'Press [ESC] to cancel or [ENTER] to accept',
    'Name:'
]
game_over_msgs = [
    "Game Over",
    'You reached level: {level_count}',
    'Press {exit}[SPACE] to restart'.format(exit=('' if IS_WEB else '[ESC] to quit or ')),
]

help_msgs = [
    "[ARROWS] - to move",
    "[s] - show highscore",
    ('' if IS_WEB else '[ESC] - exit'),
    "",
    "*** CHEATS/DEBUG ***",
    "[SPACE] - new maze",
    "[m] - show enemy",
    "[a] - activate enemies",
    "[p] - show enemy path",
    "[e] - show exit",
    "[o] - show potions",
]

VISION_RANGE: int = 4
fov_computer = None


random_maze = None
game_state = {
            "visibility_m": None,
            "enemies_pos2type": dict(),
            # "equipped_spell": None,
            # "owned_spells": set()
        }


CELL_SIDE = 32  # px
MAZE_SIZE = (24, 23)
WALL_COLOR = (8, 8, 24)
HIDDEN_CELL_COLOR = (24, 24, 24)
# user_name input label colors
COLOR_INACTIVE = 'yellow4' # shared.HIDDEN_CELL_COLOR # pygame.Color('lightskyblue3')
COLOR_ACTIVE = 'yellow' # pygame.Color('dodgerblue2')

SCR_WIDTH = 960
SCR_HEIGHT = 720

# extra const
GRID_REZ = (CELL_SIDE, CELL_SIDE)

AVATAR = None

PLAYER_DMG = 10
PLAYER_HP = 100

MONSTER_DMG = 10
MONSTER_HP = 10
MONSTER = None
TILESET = None
# two glvars for a quick n dirty bugfix (js web cxt)
joker_tile = None
pot_tile = None
exit_tile = None

WALL_TILE_RANK = 912
EXIT_TILE_RANK = 1092
UNKNOWN_TILE_RANK = 811
POISON_TILE_RANK = 810
HEAL_TILE_RANK = 783

POTION_DMG = 20
MAX_POTIONS = 4
MAX_MONSTERS = 4
SHOW_HELP = False
SHOW_HIGHSCORE = False
# CHEATS/DEBUG
EXIT_VISIBLE = False
ALL_POTIONS_VISIBLE = False
ALL_MONSTERS_VISIBLE = False
ALL_MONSTERS_PATH_VISIBLE = False
# if any of the above features is used, highscore won't be saved
CHEAT_USED = False

walkable_cells = []  # List to store walkable cells
level_count = 1
messages = []

sys_iterator = 0
