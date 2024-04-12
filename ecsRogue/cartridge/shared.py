# from . import gamejoltapi

show_input = False
user_name_input = None 
user_name = None 

fonts = {}
### TODO: Highscore WIP
# go to https://gamejolt.com/
# create account
# crate new game
GAME_VER = "0.9"
GAME_ID = "<YOUR_GAME_ID>"
PRIVATE_KEY = "YOUR_KEY"
gamejoltapi = None
TEST_SCORE_TABLE_ID = 0 # create test score table and enter it's id here
PROD_SCORE_TABLE_ID = 0 # open default score table and enter it's id here
SCORE_TABLE = []

screen = None
is_game_over = False
status_label = None

game_over_msgs_hs = [
    "Game Over",
    'You reached level : {level_count}',
    'Provide your name for highscore table',
    'Press [q] to cancel or [ENTER] to accept',
    'Name:'
]
game_over_msgs = [
    "Game Over",
    'You reached level: {level_count}',
    'Press [q] to quit or [SPACE] to restart',
]

help_msgs = [
    "[ARROWS] - to move",
    # "[s] - show highscore",
    "[q] - exit",
    "[SPACE] - new maze",
    "",
    "*** CHEATS/DEBUG ***",
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
EXIT_VISIBLE = False
ALL_POTIONS_VISIBLE = False
ALL_MONSTERS_VISIBLE = False
ALL_MONSTERS_PATH_VISIBLE = False

walkable_cells = []  # List to store walkable cells
level_count = 1
messages = []

sys_iterator = 0