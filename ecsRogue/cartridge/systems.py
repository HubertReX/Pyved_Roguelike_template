from datetime import datetime
import asyncio
# import aiohttp
# import json
import inspect
import random

from . import pimodules
from . import shared
from . import world

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

### TODO: Highscore WIP
# async def _urlopen_async(url):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             return await response.json()


#MARK: pg_event_proces_sys
def pg_event_proces_sys():
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    if shared.is_game_over:
        ### TODO: Highscore WIP
        # if shared.show_input:       
        #     for event in pg.event.get():
        #         shared.user_name_input.handle_event(event)
        #     shared.user_name_input.update()
        #     if not shared.show_input:
        #         if shared.user_name:
        #             extra_info = {
        #                 "game_ver": shared.GAME_VER,
        #                 "time_played": "n/a"
        #             }
        #             shared.gamejoltapi.scoresAdd(
        #                 f"level {shared.level_count}", 
        #                 shared.level_count, 
        #                 shared.TEST_SCORE_TABLE_ID, 
        #                 shared.user_name, 
        #                 # json.dumps(extra_info)
        #             )
        #         player = pyv.find_by_archetype('player')[0]
        #         player['health_point'] = shared.PLAYER_HP
                
        for ev in pg.event.get():
            if ev.type == pg.KEYDOWN:
                if ev.key in [pg.K_ESCAPE, pg.K_q]:
                    pyv.vars.gameover = True
                elif ev.key == pg.K_SPACE:
                    # use flag so we we'll reset level, soon in the future
                    shared.is_game_over = False
                    shared.level_count = 1
                    shared.messages = []
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
                pyv.vars.gameover = True
            elif ev.key == pg.K_UP:
                player_pos[1] -= 1
                _player_push(1)
            elif ev.key == pg.K_DOWN:
                player_pos[1] += 1
                _player_push(3)

            elif ev.key == pg.K_LEFT:
                player_pos[0] -= 1
                _player_push(2)

            elif ev.key == pg.K_RIGHT:
                player_pos[0] += 1
                _player_push(0)

            ### TODO: Highscore WIP
            # elif ev.key == pg.K_s:
            #     shared.SHOW_HIGHSCORE= not shared.SHOW_HIGHSCORE
            elif ev.key == pg.K_h:
                shared.SHOW_HELP = not shared.SHOW_HELP
            elif ev.key == pg.K_e:
                shared.EXIT_VISIBLE = not shared.EXIT_VISIBLE
            elif ev.key == pg.K_o:
                shared.ALL_POTIONS_VISIBLE = not shared.ALL_POTIONS_VISIBLE
            elif ev.key == pg.K_m:
                shared.ALL_MONSTERS_VISIBLE = not shared.ALL_MONSTERS_VISIBLE
            elif ev.key == pg.K_p:
                shared.ALL_MONSTERS_PATH_VISIBLE = not shared.ALL_MONSTERS_PATH_VISIBLE
            elif ev.key == pg.K_a:
                # toggle active on all monsters
                monsters = pyv.find_by_archetype('monster')
                for monster in monsters:
                    monster['active'] = not monster['active']
                # monster_ai_sys()
                world.update_vision_and_mobs(player_pos[0], player_pos[1])
                # _draw_all_mobs(shared.screen)
            elif ev.key == pg.K_SPACE:
                # use flag so we we'll reset level, soon in the future
                player = pyv.find_by_archetype('player')[0]
                player['enter_new_map'] = True

#MARK: world_generation_sys
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
                if pos not in [player['position']] + [monster['position'] for monster in monsters] + [exit_ent['position']]:
                    break
            world.create_potion(pos, effect)


#MARK: gamestate_update_sys            
def gamestate_update_sys():
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    player = pyv.find_by_archetype('player')[0]
    # classic_ftsize = 38
    ft = shared.fonts[38] # pyv.pygame.font.Font(None, classic_ftsize)
    if player['health_point'] <= 0 and (not shared.is_game_over):
        shared.messages.append("Game over")
        shared.is_game_over = True

        player['health_point'] = shared.PLAYER_HP        
        ### TODO: Highscore WIP
        # shared.user_name_input.active = True
        # shared.show_input = True
        
        # shared.end_game_label0 = ft.render('Game Over', True, 'yellow', 'black')
        # shared.end_game_label1 = ft.render(f'You reached Level : {shared.level_count}', True, 'yellow', 'black')
        # shared.end_game_label2 = ft.render('Press [ESC] to exit or [SPACE] to restart', True, 'yellow', 'black')
    
    monsters_cnt = len(pyv.find_by_archetype('monster')) 
    potions = pyv.find_by_archetype('potion')
    potions_cnt = 0
    for potion in potions:
        if potion['effect'] in ["Heal", "Poison"]:
            potions_cnt += 1
    shared.status_label = ft.render(f'Level: {shared.level_count}   Health: {player["health_point"]}/{shared.PLAYER_HP}   Monsters left: {monsters_cnt}   Potions left: {potions_cnt}    [h] - help', True, (255, 255, 0), 'black')

def render_messages(scr):
    classic_ftsize = 24
    # render_rows_of_text(scr, 22*32, 24, classic_ftsize, shared.help_msgs)
    ft = shared.fonts[classic_ftsize] # pyv.pygame.font.Font(None, classic_ftsize)
    for i, msg in enumerate(shared.messages[::-1][:12]):
        label = ft.render(msg, True, 'yellow', 'black')
        scr.blit(label, (22*32, shared.SCR_HEIGHT - ((i+1) * classic_ftsize)))

def render_help(scr):
    classic_ftsize = 24
    render_rows_of_text(scr, 22*32, 38, classic_ftsize, shared.help_msgs)

def render_rows_of_text(scr, x, y, font_size, msgs,  text_color='yellow', bg_color='black'):
    ft = shared.fonts[font_size] # pyv.pygame.font.Font(None, font_size)
    for i, msg in enumerate(msgs):
        label = ft.render(msg, True, text_color, bg_color)
        scr.blit(label, (x, (y + (i * font_size))))
    
async def get_score_table():
    # res = await _urlopen_async("https://postman-echo.com/delay/2")
    # print(res)
    # return
    
    # get top 10 scores
    # print("gamejoltapi.scoresFetch")
    scores_payload = await shared.gamejoltapi.scoresFetch(10, shared.TEST_SCORE_TABLE_ID)
    # print(scores_payload)
    shared.SCORE_TABLE = []
    if scores_payload["success"]:
        shared.SCORE_TABLE.append(["Rank", "Name", "Level", "Date"])
        # print(scores_payload["scores"][0])
        for rank, score in enumerate(scores_payload["scores"]):
            ts = f"{datetime.fromtimestamp(score['stored_timestamp'])}"
            shared.SCORE_TABLE.append([str(rank+1), score["guest"], score["sort"], ts])
    else:
        shared.SCORE_TABLE.append("Highscore table temporally unavailable")

def render_score_table(scr):
    # asyncio.run(get_score_table())
    # return     
    if len(shared.SCORE_TABLE) == 0:
        # get_score_table()
        asyncio.run(get_score_table())
        
    if len(shared.SCORE_TABLE) == 1:
        render_rows_of_text(scr, 50, 50, 38, shared.SCORE_TABLE)
    else:
        font_size = 38
        ft = shared.fonts[font_size]
        columns_x = [50, 50+80, 50+80+200, 50+80+250+80,]
        for j, row in enumerate(shared.SCORE_TABLE):
            # print(row)
            for i, x in enumerate(columns_x):
                label = ft.render(row[i], True, 'yellow', 'black')
                scr.blit(label, (x, (100 + (j * font_size))))


#MARK: rendering_sys
def rendering_sys():
    # print(f"{shared.sys_iterator=} {inspect.stack()[0][3]} {saved_player_pos}")
    global tileset
    
    scr = pyv.surface_create((shared.SCR_WIDTH, shared.SCR_HEIGHT))
    scr.fill(shared.WALL_COLOR)

    # ----------
    #  draw tiles
    # ----------
    nw_corner = (0, 0)
    tmp_r4 = [None, None, None, None]
    tile = shared.TILESET.image_by_rank(shared.WALL_TILE_RANK)
    dim = world.get_terrain().get_size()
    for i in range(dim[0]):
        for j in range(dim[1]):
            # ignoring walls
            tmp = world.get_terrain().get_val(i, j)
            if tmp is None:
                continue

            tmp_r4[0], tmp_r4[1] = nw_corner
            tmp_r4[0] += i * shared.CELL_SIDE
            tmp_r4[1] += j * shared.CELL_SIDE
            tmp_r4[2] = tmp_r4[3] = shared.CELL_SIDE
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
        _draw_all_mobs(scr)
        render_messages(scr)
        if shared.SHOW_HELP:
            render_help(scr)
    view = shared.screen
    view.fill(shared.WALL_COLOR)
    # lw, lh = shared.status_label.get_size()
    view.blit(scr, (0, 5))
    view.blit(shared.status_label, (0,0))
    # shared.menu.mainloop(view)
    if shared.SHOW_HIGHSCORE:
        render_score_table(view)
    if shared.show_input:
        shared.user_name_input.draw(view)


#MARK: physics_sys
def physics_sys():
    """
    implements the monster attack mechanic
    + it also proc any effect on the player based on what happened (potion, exit door etc)
    """
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
                player['health_point'] = 100
                shared.messages.append(f"Healed (full HP)")
                # print(f"HP :{player['health_point']}")
                potion['effect'] = 'disabled'
            elif potion['effect'] == 'Poison':
                player['health_point'] -= shared.POTION_DMG
                shared.messages.append(f"Poison (-{shared.POTION_DMG}HP)")
                # print(f"HP :{player['health_point']}")
                potion['effect'] = 'disabled'

#MARK: monster_ai_sys
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
                        monster['position'][0], monster['position'][1] = new_pos  # TODO a proper "kick the player" feat.
                elif len(pathfinding_result) == 1:
                    pass
                    # print(f"1 step {pathfinding_result=} {curr_pos=}")


# ----------------------------
#  private/utility functions
# ----------------------------
def _draw_all_mobs(scrref):
    player = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')
    # ----------
    #  draw player/enemies
    # ----------
    av_i, av_j = player['position']
    exit_ent = pyv.find_by_archetype('exit')[0]
    potions = pyv.find_by_archetype('potion')
    # tuile = shared.TILESET.image_by_rank(912)
    
    # exit
    if shared.game_state['visibility_m'].get_val(*exit_ent['position']) or shared.EXIT_VISIBLE:
        scrref.blit(shared.TILESET.image_by_rank(shared.EXIT_TILE_RANK),
                    (exit_ent['position'][0] * shared.CELL_SIDE, exit_ent['position'][1] * shared.CELL_SIDE, shared.CELL_SIDE, shared.CELL_SIDE))
    
    # potions
    for potion in potions:
        if shared.game_state['visibility_m'].get_val(*potion['position']) or shared.ALL_POTIONS_VISIBLE:
            # print("show potion")
            if potion['effect'] == 'Heal':
                img_index = shared.HEAL_TILE_RANK if shared.ALL_POTIONS_VISIBLE else shared.UNKNOWN_TILE_RANK
                # scrref.blit(shared.TILESET.image_by_rank(783), (potion['position'][0] * shared.CELL_SIDE, potion['position'][1] * shared.CELL_SIDE, shared.CELL_SIDE, shared.CELL_SIDE))
            elif potion['effect'] == 'Poison':
                img_index = shared.POISON_TILE_RANK if shared.ALL_POTIONS_VISIBLE else shared.UNKNOWN_TILE_RANK
            else:
                continue
            scrref.blit(
                shared.TILESET.image_by_rank(img_index), 
                (potion['position'][0] * shared.CELL_SIDE, potion['position'][1] * shared.CELL_SIDE, shared.CELL_SIDE, shared.CELL_SIDE))

    # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
    proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
    targx, targy = proj_function(av_i, av_j)
    scrref.blit(shared.AVATAR, (targx, targy, shared.CELL_SIDE, shared.CELL_SIDE))
    # ----- enemies
    # for enemy_info in shared.game_state["enemies_pos2type"].items():
    for monster in monsters:
        pos = monster['position']
        # pos, t = enemy_info
        if not shared.game_state['visibility_m'].get_val(*pos) and not shared.ALL_MONSTERS_VISIBLE:
            continue
        en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
        if shared.ALL_MONSTERS_PATH_VISIBLE:
            pg.draw.rect(scrref, monster['color'], (en_i, en_j, shared.CELL_SIDE, shared.CELL_SIDE))
            if len(monster['path']) > 1:
                delta_x = (monster['no'] // 4) * 8
                delta_y = (int(monster['no'] % 4)) * 8
                for path_pos in monster['path'][1:-1]:
                    pg.draw.rect(scrref, monster['color'], ((path_pos[0]* shared.CELL_SIDE)+4+delta_x, (path_pos[1]* shared.CELL_SIDE)+4+delta_y, 4, 4))        
        scrref.blit(shared.MONSTER, (en_i, en_j, shared.CELL_SIDE, shared.CELL_SIDE))


def _player_push(directio):
    player = pyv.find_by_archetype('player')[0]
    # monsters = pyv.find_by_archetype('monster')  # TODO kick mob feat. here?
    if (player['position'][0], player['position'][1]) not in shared.walkable_cells:
        # print('kick')
        # shared.messages.append("Wall")
        deltas = {
            0: (+1, 0),
            1: (0, -1),
            2: (-1, 0),
            3: (0, +1)
        }
        player['position'][0] -= deltas[directio][0]
        player['position'][1] -= deltas[directio][1]
    # Update player vision
    world.update_vision_and_mobs(player['position'][0], player['position'][1])
