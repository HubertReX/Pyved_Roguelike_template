# import inspect
import random

from . import pimodules
from . import shared
from . import world
from .util import prepare_desktop_score, prepare_web_score, render_messages, render_help, render_rows_of_text, render_score_table, get_wall_tile
from .util import world, player_push, draw_all_mobs

__all__ = [
    'pg_event_proces_sys',
    'world_generation_sys',
    'gamestate_update_sys',
    'monster_ai_sys',
    'physics_sys',
    'rendering_sys',
]


# aliases
pyv = pimodules.pyved_engine
pg = pyv.pygame
Sprsheet = pyv.gfx.Spritesheet
BoolMatrx = pyv.e_struct.BoolMatrix

# global vars
tileset = None
saved_player_pos = [None, None]


# MARK: pg_event_proces_sys
def pg_event_proces_sys():
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    if shared.is_game_over:
        ### TODO: Highscore WIP
        if shared.show_input:       
            for event in pg.event.get():
                shared.user_name_input.handle_event(event)
            shared.user_name_input.update()
            if not shared.show_input:
                if shared.user_name:
                    if shared.CHEAT_USED:
                        shared.messages.append("Cheat used - no highscore")
                    else:
                        if shared.IS_WEB:
                            prepare_web_score()
                        else:
                            prepare_desktop_score()
                player = pyv.find_by_archetype('player')[0]
                player['health_point'] = shared.PLAYER_HP
                
        for ev in pg.event.get():
            if ev.type == pg.KEYDOWN:
                if ev.key in [pg.K_ESCAPE, pg.K_q]:
                    # ending game in WEB doesn't make sense (the game freezes)
                    if not shared.IS_WEB or shared.USE_HIGHSCORE_STUB:
                        pyv.vars.gameover = True
                elif ev.key == pg.K_SPACE:
                    # use flag so we we'll reset level, soon in the future
                    shared.is_game_over = False
                    shared.level_count = 1
                    shared.CHEAT_USED = False
                    shared.ALL_MONSTERS_PATH_VISIBLE = False
                    shared.ALL_MONSTERS_VISIBLE = False
                    shared.ALL_POTIONS_VISIBLE = False
                    shared.EXIT_VISIBLE = False
                    # shared.messages = []
                    shared.messages.append("-- NEW GAME --")
                    pyv.vars.gameover = False
                    player = pyv.find_by_archetype('player')[0]
                    player['enter_new_map'] = True
                    player['health_point'] = shared.PLAYER_HP
        return

    player_pos = pyv.find_by_archetype('player')[0]['position']
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN:
            # print(ev.key, pg.K_ESCAPE)
            if ev.key in [pg.K_ESCAPE, pg.K_q]:
                # ending game in WEB doesn't make sense (the game freezes)
                if not shared.IS_WEB or shared.USE_HIGHSCORE_STUB:
                    pyv.vars.gameover = True
            elif ev.key == pg.K_UP:
                player_pos[1] -= 1
                player_push(1)
            elif ev.key == pg.K_DOWN:
                player_pos[1] += 1
                player_push(3)

            elif ev.key == pg.K_LEFT:
                player_pos[0] -= 1
                player_push(2)

            elif ev.key == pg.K_RIGHT:
                player_pos[0] += 1
                player_push(0)

            ### TODO: Highscore WIP
            elif ev.key == pg.K_s:
                shared.SHOW_HIGHSCORE= not shared.SHOW_HIGHSCORE
            elif ev.key == pg.K_h:
                shared.SHOW_HELP = not shared.SHOW_HELP
            elif ev.key == pg.K_e:
                shared.EXIT_VISIBLE = not shared.EXIT_VISIBLE
                shared.CHEAT_USED = True
            elif ev.key == pg.K_o:
                shared.ALL_POTIONS_VISIBLE = not shared.ALL_POTIONS_VISIBLE
                shared.CHEAT_USED = True
            elif ev.key == pg.K_m:
                shared.ALL_MONSTERS_VISIBLE = not shared.ALL_MONSTERS_VISIBLE
                shared.CHEAT_USED = True
            elif ev.key == pg.K_p:
                shared.ALL_MONSTERS_PATH_VISIBLE = not shared.ALL_MONSTERS_PATH_VISIBLE
                shared.CHEAT_USED = True
            elif ev.key == pg.K_a:
                # toggle active on all monsters
                shared.CHEAT_USED = True
                monsters = pyv.find_by_archetype('monster')
                for monster in monsters:
                    monster['active'] = not monster['active']
                # monster_ai_sys()
                world.update_vision_and_mobs(player_pos[0], player_pos[1])
                # draw_all_mobs(shared.screen)
            elif ev.key == pg.K_SPACE:
                shared.CHEAT_USED = True
                # use flag so we we'll reset level, soon in the future
                player = pyv.find_by_archetype('player')[0]
                player['enter_new_map'] = True


# MARK: world_generation_sys
def world_generation_sys():
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    player = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')
    potions = pyv.find_by_archetype('potion')
    exit_ent = pyv.find_by_archetype('exit')[0]

    if player['enter_new_map']:
        player['enter_new_map'] = False
        # pl_ent['health_point'] = shared.PLAYER_HP
        # print('Level generation...')
        # print(f'HP:{pl_ent["health_point"]}')

        w, h = shared.MAZE_SIZE
        shared.random_maze = pyv.rogue.RandomMaze(w, h, min_room_size=3, max_room_size=5)
        shared.wall_type = random.choice(list(shared.WALLS_TERRAIN_SETS.keys()))
        # print(shared.game_state['rm'].blocking_map)

        # IMPORTANT: adding mobs comes before computing the visibility
        shared.game_state["enemies_pos2type"].clear()
        for monster in monsters:
            pyv.delete_entity(monster)

        for i in range(shared.MAX_MONSTERS + shared.level_count - 1):
            tmp = shared.random_maze.pick_walkable_cell()
            pos_key = tuple(tmp)
            shared.game_state["enemies_pos2type"][pos_key] = 1  # all enemies type=1
            world.create_monster(tmp, i)

        # - comp. the visibility
        shared.game_state["visibility_m"] = BoolMatrx((w, h))
        shared.walkable_cells = []
        shared.game_state['visibility_m'].set_all(False)
        pyv.find_by_archetype('player')[0]['position'] = shared.random_maze.pick_walkable_cell()
        world.update_vision_and_mobs(
            pyv.find_by_archetype('player')[0]['position'][0],
            pyv.find_by_archetype('player')[0]['position'][1]
        )

        # add-on?
        # add exit
        while True:
            exitPos = shared.random_maze.pick_walkable_cell()
            if exitPos not in [player['position']] + [monster['position'] for monster in monsters]:
                exit_ent['position'] = exitPos
                break

        # add potions

        for potion in potions:
            pyv.delete_entity(potion)

        for _ in range(shared.MAX_POTIONS):
            effect = random.choice(["Heal", "Poison"])
            while True:
                pos = shared.random_maze.pick_walkable_cell()
                if pos not in [player['position']] + [monster['position'] for monster in monsters] + [
                    exit_ent['position']]:
                    break
            world.create_potion(pos, effect)


# MARK: gamestate_update_sys
def gamestate_update_sys():
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    player = pyv.find_by_archetype('player')[0]
    # classic_ftsize = 38
    ft = shared.fonts[38]  # pyv.pygame.font.Font(None, classic_ftsize)
    if player['health_point'] <= 0 and (not shared.is_game_over):
        shared.messages.append("*** Game over ***")
        shared.is_game_over = True

        # player['health_point'] = shared.PLAYER_HP
        ### TODO: Highscore WIP
        if shared.CHEAT_USED:
            # no highscore
            player['health_point'] = shared.PLAYER_HP
            shared.messages.append("Cheat used - no highscore")
        else:
            shared.user_name_input.active = True
            shared.show_input = True
        
    
    monsters_cnt = len(pyv.find_by_archetype('monster')) 
    potions = pyv.find_by_archetype('potion')
    potions_cnt = 0
    for potion in potions:
        if potion['effect'] in ["Heal", "Poison"]:
            potions_cnt += 1
    shared.status_label = ft.render(f'Level: {shared.level_count}   Health: {player["health_point"]}/{shared.PLAYER_HP}   Monsters left: {monsters_cnt}   Potions left: {potions_cnt}    [h] - help', True, (255, 255, 0), 'black')


# MARK: rendering_sys
def rendering_sys():
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    global tileset
    # scr = pyv.surface_create((shared.SCR_WIDTH, shared.SCR_HEIGHT))
    scr = shared.screen
    scr.fill(shared.WALL_COLOR)

    # ----------
    #  draw tiles
    # ----------
    nw_corner = (0, 0)
    tmp_r4 = [None, None, None, None]

    # TODO if u can fix to use tileset?
    # tile = shared.TILESET.image_by_rank(shared.WALL_TILE_RANK)
    tile = shared.joker_tile

    dim = world.get_terrain().get_size()
    for i in range(dim[0]):
        for j in range(dim[1]):
            tmp_r4[0], tmp_r4[1] = nw_corner
            tmp_r4[0] += i * shared.CELL_SIDE
            tmp_r4[1] += j * shared.CELL_SIDE
            tmp_r4[2] = tmp_r4[3] = shared.CELL_SIDE

            # draw walls 
            # TODO: the calculation of wall tile should be moved to world_generation_sys so it's done only once not witch each frame
            tmp = world.get_terrain().get_val(i, j)
            if tmp is None:                
                tile_id = get_wall_tile(i, j, shared.wall_type)
                wall = shared.TILESET[f"{tile_id}.png"]
                if not world.can_see((i, j)):  # hidden cell
                    pg.draw.rect(scr, 'black', tmp_r4)
                else:
                    scr.blit(tile, tmp_r4)
                    scr.blit(wall, tmp_r4)
                continue

            if not world.can_see((i, j)):  # hidden cell

                pg.draw.rect(scr, shared.HIDDEN_CELL_COLOR, tmp_r4)
            else:  # visible tile
                scr.blit(tile, tmp_r4)
                shared.walkable_cells.append((i, j))

    if shared.is_game_over:
        if shared.show_input:
            game_over_msgs = [msg.format(level_count=shared.level_count) for msg in shared.game_over_msgs_hs]
        else:
            game_over_msgs = [msg.format(level_count=shared.level_count) for msg in shared.game_over_msgs]

        render_rows_of_text(scr, 50, 50, 38, game_over_msgs)
        render_messages(scr)

        # lw, lh = shared.end_game_label0.get_size()
        # scr.blit(
        #     shared.end_game_label0, ((shared.SCR_WIDTH - lw) // 2, (shared.SCR_HEIGHT - lh) // 3)
        # )
        # lw, lh = shared.end_game_label1.get_size()
        # scr.blit(
        #     shared.end_game_label1, ((shared.SCR_WIDTH - lw) // 2, (shared.SCR_HEIGHT - lh) // 2)
        # )
        # lw, lh = shared.end_game_label2.get_size()
        # scr.blit(
        #     shared.end_game_label2, ((shared.SCR_WIDTH - lw) // 2, 2* (shared.SCR_HEIGHT - lh) // 3)
        # )
    else:
        draw_all_mobs(scr)
        render_messages(scr)
        if shared.SHOW_HELP:
            render_help(scr)

    # Re-enable this when the BUG temp surface [custom buffer] webctx is fixed
    # view = shared.screen
    # view.fill(shared.WALL_COLOR)

    # lw, lh = shared.status_label.get_size()

    # before:
    # view.blit(scr, (0, 5))
    # view.blit(shared.status_label, (0, 0))
    # after:
    scr.blit(shared.status_label, (0, 0))

    # remove this line whene the BUG temp surface [custom buffer] webctx is fixed
    view = scr
    if shared.SHOW_HIGHSCORE:
        render_score_table(view)
    if shared.show_input:
        shared.user_name_input.draw(view)


# MARK: physics_sys
def physics_sys():
    """
    implements the monster attack mechanic
    + it also proc any effect on the player based on what happened (potion, exit door etc)
    """
    if shared.is_game_over:
        return
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    player = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')
    exit_ent = pyv.find_by_archetype('exit')[0]
    potions = pyv.find_by_archetype('potion')
    shared.sys_iterator += 1

    monsters_to_del = []
    for monster in monsters:
        if monster['position'] == player['position']:
            # print(f" {shared.sys_iterator=} {monster['no']}")
            monster['health_point'] -= player['damages']
            player['health_point'] -= monster['damages']
            shared.messages.append(f"Got hit (-{monster['damages']}HP)")
            # print(f"HP :{player['health_point']}")
            if monster['health_point'] < 0:
                monsters_to_del.append(monster)
                # pyv.delete_entity(monster)
            if player['health_point'] < 0:
                player['health_point'] = 0
    for monster in monsters_to_del:
        pyv.delete_entity(monster)

    if player['position'] == exit_ent['position']:
        player['enter_new_map'] = True
        shared.level_count += 1
        shared.messages.append(f"*** Level {shared.level_count} ***")
        # print('YOU REACHED LEVEL : ' + str(shared.level_count))

    for potion in potions:
        if player['position'] == potion['position']:
            if potion['effect'] == 'Heal':
                player['health_point'] = shared.PLAYER_HP
                shared.messages.append(f"Healed (full HP)")
                # print(f"HP :{player['health_point']}")
                potion['effect'] = 'disabled'
            elif potion['effect'] == 'Poison':
                player['health_point'] -= shared.POTION_DMG
                shared.messages.append(f"Poison (-{shared.POTION_DMG}HP)")
                if player['health_point'] < 0:
                    player['health_point'] = 0
                
                # print(f"HP :{player['health_point']}")
                potion['effect'] = 'disabled'


# MARK: monster_ai_sys
def monster_ai_sys():
    global saved_player_pos
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    i, j = saved_player_pos
    player = pyv.find_by_archetype('player')[0]
    # monsters = pyv.find_by_archetype('monster')
    curr_pos = player['position']

    if (i is None) or curr_pos[0] != i or curr_pos[1] != j:
        # position has changed!
        saved_player_pos[0], saved_player_pos[1] = curr_pos
        blockmap = shared.random_maze.blocking_map
        monsters = pyv.find_by_archetype('monster')
        for monster in monsters:
            if not monster['active']:
                pass
            else:
                pathfinding_result = pyv.terrain.DijkstraPathfinder.find_path(
                    blockmap, monster['position'], player['position']
                )
                monster['path'] = pathfinding_result
                # steps_cnt = len(pathfinding_result)
                if len(pathfinding_result) >= 2:
                    new_pos = pathfinding_result[1]  # index 1 --> 1 step forward!
                    # print(f"2 steps {pathfinding_result=} {curr_pos=}")
                    if new_pos not in [other_monster['position'] for other_monster in monsters]:
                        # print('pos not taken', new_pos)
                        monster['position'][0], monster['position'][
                            1] = new_pos  # TODO a proper "kick the player" feat.
                elif len(pathfinding_result) == 1:
                    pass
                    # print(f"1 step {pathfinding_result=} {curr_pos=}")
