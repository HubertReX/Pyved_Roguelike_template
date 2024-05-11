import random
from . import shared
from . import pimodules
from .shared import monster_types, monster_dmg_amount, monster_hitpoints

pyv = pimodules.pyved_engine
pyv.bootstrap_e()
pygame = pyv.pygame


def start_game():
    shared.user_name = shared.user_name_input.get_value()
    shared.show_input = False
    shared.menu.disable()


def create_player():
    player = pyv.new_from_archetype('player')
    pyv.init_entity(player, {
        'position': None,
        'controls': {'left': False, 'right': False, 'up': False, 'down': False},
        'damages': shared.PLAYER_DMG,
        'health_point': shared.PLAYER_HP,
        'enter_new_map': True,
    })


# def create_wall():
#     wall = pyv.new_from_archetype('wall')
#     pyv.init_entity(wall, {})


def create_monster(position, no):
    monster = pyv.new_from_archetype('monster')
    mtype = random.choice(monster_types.all_codes)
    pyv.init_entity(monster, {
        'position': position,
        'type': mtype,
        'dmg': monster_dmg_amount.get(mtype, monster_dmg_amount[-1]),
        'health_point': monster_hitpoints.get(mtype, monster_hitpoints[-1]),
        'no': no,
        'color': (random.randint(20, 255), random.randint(20, 255), random.randint(20, 255)),
        'path': [],
        'active': False  # the mob will become active, once the player sees it
    })


def create_potion(position, effect):
    potion = pyv.new_from_archetype('potion')
    pyv.init_entity(potion, {
        'position': position,
        'effect': effect
    })


def create_exit():
    exit_ent = pyv.new_from_archetype('exit')
    pyv.init_entity(exit_ent, {})


def get_terrain():
    return shared.random_maze.getMatrix()


def update_vision_and_mobs(i, j):
    if shared.fov_computer is None:
        shared.fov_computer = pyv.rogue.FOVCalc()

    shared.game_state['visibility_m'].set_val(i, j, True)

    def func_visibility(a, b):
        if shared.game_state['visibility_m'].is_out(a, b):
            return False
        if shared.random_maze.getMatrix().get_val(a, b) is None:  # cannot see through walls
            return False
        return True

    li_visible = shared.fov_computer.calc_visible_cells_from(i, j, shared.VISION_RANGE, func_visibility)

    for c in li_visible:
        shared.game_state['visibility_m'].set_val(c[0], c[1], True)

    # we also need to update the state of mobs!
    all_mobs = pyv.find_by_archetype('monster')
    for monster in all_mobs:
        if tuple(monster['position']) in li_visible:
            monster['active'] = True  # mob "activation" --> will track the player
            # print('mob activation ok')


def can_see(cell):
    # print( shared.game_state['visibility_m'])
    return shared.game_state['visibility_m'].get_val(*cell)


def get_all_walkable_cells():
    w, h = shared.MAZE_SIZE  # Update these dimensions to match your map size
    walkable_cells = []

    for i in range(w):
        for j in range(h):
            cell = (i, j)
            walkable_cells.append(cell)

    return walkable_cells
