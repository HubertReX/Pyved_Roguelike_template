from . import pimodules
from . import shared
from . import systems
from . import world
from .util import clear_local_score_table
# from pygame_menu.examples import create_example_window

# from . import gamejoltapi
if not shared.IS_WEB:
    import gamejoltapi

pyv = pimodules.pyved_engine
pygame = pyv.pygame


"""
Readability Buff:
if the world.py contains info about the game MODEL, it's better to init data related to graphics elsewhere,
or just here in the main file
"""
from .classes import InputBox


Spritesheet = pyv.gfx.Spritesheet  # TODO avoid using this, prefer using pyv pre-built spritesheet loading mechanism


def init_images():
    grid_rez = (32, 32)

    img = pyv.vars.images['tileset']
    shared.joker_tile = pygame.Surface((32, 32))
    shared.joker_tile.fill(pyv.pal.japan['peach'])
    shared.exit_tile = pyv.vars.images['exit_tile']
    shared.pot_tile = pyv.vars.images['pot_tile']

    # TODO: can fix this in js web ctx?
    # tileset = Spritesheet(img, 2)  # use upscaling x2
    # tileset.set_infos(grid_rez)
    #shared.TILESET = tileset

    # old avatar:
    # img = pyv.vars.images['avatar1']
    # planche_avatar = Spritesheet(img, 2)  # upscaling x2
    # planche_avatar.set_infos(grid_rez)
    # planche_avatar.colorkey = (255, 0, 255)

    monster_img = pyv.vars.images['monster']

    # old avatar:
    # shared.AVATAR = planche_avatar.image_by_rank(0)
    # new avatar:
    avatar_spr_sheet = pyv.vars.spritesheets['smallninja_sprites']
    shared.AVATAR = avatar_spr_sheet['av0.png']

    shared.MONSTER = monster_img


def load_fonts():
    font_sizes = [24, 38]
    for font_size in font_sizes:
        shared.fonts[font_size] = pyv.pygame.font.Font(None, font_size)


def init_menu():
    # import pygame_menu
    # pygame_menu_ce not working with pygbag:
    #   File "/data/data/ecsrogue/assets/cartridge/systems.py", line 266, in rendering_sys
    #     shared.menu.draw(view)
    #   File "/data/data/org.python/assets/build/env/pygame_menu/menu.py", line 2117, in draw
    #     self._current._menubar.draw(surface)
    #   File "/data/data/org.python/assets/build/env/pygame_menu/widgets/core/widget.py", line 1391, in draw
    #     self._draw(surface)
    #   File "/data/data/org.python/assets/build/env/pygame_menu/widgets/widget/menubar.py", line 250, in _draw
    #     gfxdraw.filled_polygon(surface, self._polygon_pos, self._background_color)
    # pygame.error: Parameter 'renderer' is invalid
    
    # shared.menu = pygame_menu.Menu(
    #     height=300,
    #     theme=pygame_menu.themes.THEME_BLUE,
    #     title='Welcome',
    #     width=400
    # )
    # shared.user_name_input = shared.menu.add.text_input('Name: ', default='', maxchar=10)
    # # menu.add.selector('Difficulty: ', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
    # shared.menu.add.button('Play', start_game)
    # shared.menu.add.button('Quit', pygame_menu.events.EXIT)
    if not shared.IS_WEB:
        if len(shared.GAME_ID) > 0 and len(shared.PRIVATE_KEY) > 0 and shared.PROD_SCORE_TABLE_ID > 0:
            shared.gamejoltapi = gamejoltapi.GameJoltAPI(
                shared.GAME_ID,
                shared.PRIVATE_KEY,
                # username=USERNAME,
                # userToken=TOKEN,
                responseFormat="json",
                submitRequests=True
            )
        else:
            print("*" * 50)
            print("GameJolt API needs proper GAME_ID, PRIVATE_KEY and PROD_SCORE_TABLE_ID to be set. See shared.py for more details.")
            print("HIGHSCORE table will be disabled.")
            print("*" * 50)

    shared.user_name_input = InputBox(135, 205, 140, 32, max_len=10)


@pyv.declare_begin
def init_game(vmst=None):
    pyv.init(wcaption='Roguata')

    screen = pyv.get_surface()
    shared.screen = screen
    pyv.define_archetype('player', (
        'position', 'controls', 'body', 'damages', 'health_point', 'enter_new_map',
    ))
    # pyv.define_archetype('wall', ('body',))
    pyv.define_archetype('monster', ('position', 'damages', 'health_point', 'active', 'color', 'path', 'no'))
    pyv.define_archetype('exit', ('position',))
    pyv.define_archetype('potion', ('position', 'effect',))

    world.create_player()
    # world.create_wall()
    world.create_exit()
    # world.create_potion()

    init_images()
    load_fonts()
    init_menu()

    # clear_local_score_table()
    pyv.bulk_add_systems(systems)


@pyv.declare_update
def upd(time_info=None):
    pyv.systems_proc()
    pyv.flip()
    # shared.sys_iterator = 0


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    # print('gameover!')
