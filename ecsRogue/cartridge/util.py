"""
Nota bene:
it's important to keep utility functions separate from sysstems.py for the a better readability
"""
from datetime import datetime
import asyncio
# import aiohttp
# import json
# import inspect
from . import shared
from . import world
from . import pimodules


# alias
pyv = pimodules.pyved_engine
pg = pyv.pygame


# TODO: Highscore WIP
# async def _urlopen_async(url):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             return await response.json()


def render_messages(scr):
    classic_ftsize = 24
    # render_rows_of_text(scr, 22*32, 24, classic_ftsize, shared.help_msgs)
    ft = shared.fonts[classic_ftsize]  # pyv.pygame.font.Font(None, classic_ftsize)
    for i, msg in enumerate(shared.messages[::-1][:12]):
        label = ft.render(msg, True, 'yellow', 'black')
        scr.blit(label, (22 * 32, shared.SCR_HEIGHT - ((i + 1) * classic_ftsize)))


def render_help(scr):
    classic_ftsize = 24
    render_rows_of_text(scr, 22 * 32, 38, classic_ftsize, shared.help_msgs)


def render_rows_of_text(scr, x, y, font_size, msgs, text_color='yellow', bg_color='black'):
    ft = shared.fonts[font_size]  # pyv.pygame.font.Font(None, font_size)
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
            shared.SCORE_TABLE.append([str(rank + 1), score["guest"], score["sort"], ts])
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
        columns_x = [50, 50 + 80, 50 + 80 + 200, 50 + 80 + 250 + 80, ]
        for j, row in enumerate(shared.SCORE_TABLE):
            # print(row)
            for i, x in enumerate(columns_x):
                label = ft.render(row[i], True, 'yellow', 'black')
                scr.blit(label, (x, (100 + (j * font_size))))


# ----------------------------
#  legacy/old (that is:initially defined by tom/alex)
#  utility functions
# ----------------------------
def draw_all_mobs(scrref):
    player = pyv.find_by_archetype('player')[0]
    monsters = pyv.find_by_archetype('monster')
    av_i, av_j = player['position']
    exit_ent = pyv.find_by_archetype('exit')[0]
    potions = pyv.find_by_archetype('potion')

    # draw the exit
    if shared.game_state['visibility_m'].get_val(*exit_ent['position']) or shared.EXIT_VISIBLE:
        if shared.TILESET:
            adhoc_exit_tile = shared.TILESET.image_by_rank(shared.EXIT_TILE_RANK)
        else:
            adhoc_exit_tile = shared.exit_tile
        scrref.blit(
            adhoc_exit_tile, (
                exit_ent['position'][0] * shared.CELL_SIDE,
                exit_ent['position'][1] * shared.CELL_SIDE,
                shared.CELL_SIDE,
                shared.CELL_SIDE
            )
        )

    # draw all potions
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
            adhoc_pot_tile = shared.TILESET.image_by_rank(img_index) if shared.TILESET else shared.pot_tile
            scrref.blit(
                adhoc_pot_tile,
                (potion['position'][0] * shared.CELL_SIDE, potion['position'][1] * shared.CELL_SIDE, shared.CELL_SIDE,
                 shared.CELL_SIDE))

    # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
    proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
    targx, targy = proj_function(av_i, av_j)
    scrref.blit(shared.AVATAR, (targx, targy, shared.CELL_SIDE, shared.CELL_SIDE))

    # draw all enemies
    for monster in monsters:
        pos = monster['position']
        # pos, t = enemy_info
        if shared.ALL_MONSTERS_VISIBLE or shared.game_state['visibility_m'].get_val(*pos):
            en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
            if shared.ALL_MONSTERS_PATH_VISIBLE:
                pg.draw.rect(scrref, monster['color'], (en_i, en_j, shared.CELL_SIDE, shared.CELL_SIDE))
                if len(monster['path']) > 1:
                    delta_x = (monster['no'] // 4) * 8
                    delta_y = (int(monster['no'] % 4)) * 8
                    for path_pos in monster['path'][1:-1]:
                        pg.draw.rect(
                            scrref, monster['color'], (
                                (path_pos[0] * shared.CELL_SIDE) + 4 + delta_x,
                                (path_pos[1] * shared.CELL_SIDE) + 4 + delta_y,
                                4, 4
                            )
                        )
            scrref.blit(shared.MONSTER, (en_i, en_j, shared.CELL_SIDE, shared.CELL_SIDE))


def player_push(directio):
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
