from . import pimodules
# from pygame_menu.examples import create_example_window


pyv = pimodules.pyved_engine
pyv.bootstrap_e()


from . import shared
from .states import *  # classes: TitleState, ExploreState


@pyv.declare_begin
def init_game(vmst=None):
    pyv.init(wcaption='Roguata')

    # because we use the gamestates mechanism, it is mandatory to activate pyv event system as well:
    ev_mger = pyv.get_ev_manager()
    ev_mger.setup()
    gs_enum = shared.GameStates

    pyv.declare_game_states(gs_enum, {
        gs_enum.TitleScreen: TitleState,
        gs_enum.Explore: ExploreState
    })

    # We need these two instruction to enforce the call to .enter() on TitleState!
    # import pyved_engine
    # pyved_engine.events.KengiEv
    # pyved_engine.EngineEvTypes
    # debug:
    # print(pyv.EngineEvTypes.inv_map)
    ev_mger.post(
        pyv.EngineEvTypes.Gamestart
    )
    ev_mger.update()


@pyv.declare_update
def upd(time_info=None):
    if pyv.curr_state() == shared.GameStates.Explore:  # hacky solution,
        # because not all gamestates uses the ECS pattern,
        # hence the test w.r.t pyv.curr_state()è
        pyv.systems_proc()
    else:
        ev_mgr = pyv.get_ev_manager()
        ev_mgr.post(pyv.EngineEvTypes.Paint, screen=pyv.vars.screen)
        tnow = time_info if time_info else pyv.vars.clock.get_time()
        ev_mgr.post(pyv.EngineEvTypes.Update, curr_t=tnow)
        ev_mgr.update()

    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
