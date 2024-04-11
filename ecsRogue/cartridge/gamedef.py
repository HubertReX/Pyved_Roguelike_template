from . import pimodules
from . import shared
from . import systems
from . import world

pyv = pimodules.pyved_engine
pygame = pyv.pygame

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
    world.init_images()
    world.load_fonts()
    world.init_menu()
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
