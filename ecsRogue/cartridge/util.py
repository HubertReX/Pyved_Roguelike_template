"""
Nota bene:
it's important to keep utility functions separate from sysstems.py for the a better readability
"""
from datetime import datetime
import asyncio
# import aiohttp
import json
import time
# import inspect
from . import shared
from . import world
from . import pimodules


# alias
pyv = pimodules.pyved_engine
pg = pyv.pygame

# --------------------------
# other
# --------------------------
def save_screenshot():
    # save current screen to SCREENSHOT_FOLDER as PNG with timestamp in name
    
    # prevent from taking screenshots in web browser
    # (it actually works, the file is saved in virtual FS 
    # and there is access to it, but I don't see a way to download it)
    if not shared.IS_WEB or shared.USE_HIGHSCORE_STUB:
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = shared.SCREENSHOT_FOLDER / f"screenshot_{time_str}.png"
        pg.image.save(shared.screen, file_name)
        shared.messages.append("screenshot saved to file")
        if shared.IS_DEBUG:
            shared.messages.append(str(file_name))


# --------------------------
# fancy walls
# --------------------------
def get_wall_tile(i, j, wall_type="big_fence"):
    # keys are 4 chars long, each digit determines if there is wall tiles next to this one
    # 1 = there is a wall
    # 0 = no wall
    # dirs are clockwise starting from north: "NESW"
    # e.g.: "0110" means there is wall to the east (right) and to the south (below)
    # dict values represent sprite id from sprite sheet
    
    COORD_OFFSET = [
        [0, -1],
        [+1, 0],
        [0, +1],
        [-1, 0],
    ]

    blocking_map = shared.random_maze.blocking_map
    key = ""
    max_w, max_h = shared.MAZE_SIZE

    for offset in COORD_OFFSET:
        pos = (i + offset[0], j + offset[1])
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= max_w  or pos[1] >= max_h:
            key += "0"
        else:
            if blocking_map.get_val(*pos):
                key += "1"
            else:
                key += "0"

    return shared.WALLS_TERRAIN_SETS[wall_type].get(key, 0)

# --------------------------
# rendering helper functions
# --------------------------
def render_messages(scr):
    # render last 12 game events in lower right part of screen
    font_size = 24
    ft = shared.fonts[font_size]
    # reverse order (printed from bottom of screen up) limit to 12 last messages
    for i, msg in enumerate(shared.messages[::-1][:12]):
        label = ft.render(str(msg), True, "yellow", "black")
        scr.blit(label, (22 * 32, shared.SCR_HEIGHT - ((i + 1) * font_size)))


def render_help(scr):
    # render help messages with key bindings in upper right part of screen
    font_size = 24
    render_rows_of_text(scr, 22 * 32, 38, font_size, shared.help_msgs)


def render_rows_of_text(scr, x, y, font_size, msgs, bg_panel=True, text_color="yellow", bg_color="black"):
    # prints rows of text, one under another in given position, with black panel as background (if bg_panel)
    ft = shared.fonts[font_size]
    if bg_panel:
        pg.draw.rect(scr, "black", [x - 5, y - 5, shared.SCR_WIDTH - 150, (len(msgs) + 1) * font_size])
        
    for i, msg in enumerate(msgs):
        label = ft.render(str(msg), True, text_color, bg_color)
        scr.blit(label, (x, (y + (i * font_size))))


def split_string(text, length):
    # cuts string into equal length chunks (e.g. to fit into panel)
    return (text[0+i:length+i] for i in range(0, len(text), length))

# --------------------------
# HIGHSCORE functions
# --------------------------


# async def _urlopen_async(url):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             return await response.json()

def get_desktop_rank():
    # extracts rank (position on highscore list) from highscore table
    # Game Jolt API version (desktop mode)
    rank = -1
    res = shared.gamejoltapi.scoresFetch(shared.NO_TOP_SCORES, shared.TEST_SCORE_TABLE_ID)
    if res["success"]:
        for i, data in enumerate(res["scores"]):
            if data["guest"] == shared.user_name:
                rank = i + 1
                break
    
    return rank

def prepare_desktop_score():
    # prepares and stores score data of current user
    # and generate messages based on old and new rank
    # Game Jolt API version (desktop mode)
    
    if not shared.gamejoltapi:
        return
    
    extra_info = {
                "game_ver": shared.GAME_VER,
                "time_played": "n/a"
    }
    old_rank = get_desktop_rank()

    shared.gamejoltapi.scoresAdd(
        f"level {shared.level_count}", 
        shared.level_count, 
        shared.TEST_SCORE_TABLE_ID, 
        shared.user_name, 
        json.dumps(extra_info)
    )
    
    new_rank = get_desktop_rank()
    add_messages_based_on_ranks(old_rank, new_rank)


def prepare_web_score():
    # prepares and stores score data of current user
    # and generate messages based on old and new rank
    # Local storage version (web browser)
    
    data = {
        "level": shared.level_count,
        "stored_timestamp": str(time.time()),
        "game_ver": shared.GAME_VER,
        "time_played": "n/a"
    }
    scores = get_scores()
    old_rank = get_score_rank(scores)
    update_score(scores, data)
    
    # if changed then store locally
    if scores[shared.user_name] == data:
        set_web_score(data)
    
    # sort and limit results to top NO_TOP_SCORES
    top_scores = get_top_scores(scores)
    # removed scores outside of top list from local stored 
    clear_worst_scores(top_scores)
    new_rank = get_score_rank(scores)
    add_messages_based_on_ranks(old_rank, new_rank)
    shared.SCORES = top_scores
    
    if shared.USE_HIGHSCORE_STUB:
        shared.HIGHSCORE_STUB = top_scores


def add_messages_based_on_ranks(old_rank, new_rank):
    # adds motivational messages depending on how did players rank in highscore table changed
    
    if new_rank == -1:
        shared.messages.append("More luck next time!")
    elif old_rank == -1: 
        if new_rank > 0:
            shared.messages.append(f"Your first rank is {new_rank}")
    else:
        if new_rank > old_rank:
            if new_rank == 1:
                shared.messages.append(f"Congrats! You're number one!")
            elif new_rank == 2:
                shared.messages.append(f"Congrats! Almost at the top!")
            elif new_rank == 3:
                shared.messages.append(f"Congrats! You're on podium!")
            else:
                shared.messages.append("You've past your previous rank")
            shared.messages.append(f"Your new rank is {new_rank}")
        else:
            shared.messages.append(f"You're previous rank was {old_rank}")


def set_web_score(data):
    # stores score data locally
    # Local storage version (web browser) or STUB
    
    if shared.USE_HIGHSCORE_STUB:
        return

    try:
        data_str = json.dumps(data)
        from platform import window
        window.localStorage.setItem(shared.user_name, data_str)
        
    except Exception as e:
        if shared.IS_DEBUG:
            e_str = str(e)
            shared.messages.append(f"Error set_web_score")
            shared.messages += split_string(e_str, 30)


def get_scores():
    # get scores from local storage
    # return empty dict if failed
    # Local storage version (web browser) or STUB
    
    if shared.USE_HIGHSCORE_STUB:
        return shared.HIGHSCORE_STUB

    try:
        from platform import window
        
        scores = {}
        for i in range(window.localStorage.length):
            user_name = window.localStorage.key(i)
            data = window.localStorage.getItem(user_name)
            score = json.loads(data)
            scores[user_name] = score
    except Exception as e:
        scores = {}
        if shared.IS_DEBUG:
            shared.messages.append(f"Error get_scores")
            s = str(e)
            shared.messages += split_string(s, 30)
    finally:
        return scores


def update_score(scores, score_data):
    # updates score only if level achieved is higher 
    # (when equal still updates to sort by timestamp or plaid time in future)
    # Local storage version (web browser) or STUB
    
    if shared.user_name in scores:
        if scores[shared.user_name]["level"] <= score_data["level"]:
            scores[shared.user_name] = score_data
    else:
        scores[shared.user_name] = score_data
    
    return scores


def get_score_rank(scores):
    # returns rank - position on highscore list (first == 1) 
    # or -1 if not listed
    # Local storage version (web browser) or STUB

    user_names = list(get_top_scores(scores).keys())
    rank = -1
    if shared.user_name in user_names:
        rank = user_names.index(shared.user_name) + 1
    return rank


def get_top_scores(scores):
    # sort descending by level, than by timestamp from earliest (time when scored) 
    # and return only top N (NO_TOP_SCORES)
    # original 'scores' dict parameter is not affected
    # Local storage version (web browser) or STUB

    return dict(sorted(scores.items(), key=lambda kv: ((-kv[1]["level"], -float(kv[1]["stored_timestamp"])), kv[0]))[:shared.NO_TOP_SCORES])


def clear_local_score_table():
    # clears score data from local storage
    # Local storage version (web browser) or STUB
    
    if shared.IS_WEB:
        try:
            from platform import window
            keys = []
            for i in range(window.localStorage.length):
                keys.append(window.localStorage.key(i))
            while keys: 
                window.localStorage.removeItem(keys.pop())
        except:
            pass


def clear_worst_scores(top_scores):
    # removes scores from local storage if not in "top_scores" dict parameter
    # (assuming "top_scores" is result of get_top_scores() )
    # Local storage version (web browser) or STUB

    if shared.USE_HIGHSCORE_STUB:
        top_user_names = top_scores.keys()
        all_user_names = list(shared.HIGHSCORE_STUB.keys())
        # users_to_clear = []
        for user_name in all_user_names:
            if user_name not in top_user_names:
                del shared.HIGHSCORE_STUB[user_name]
                
        return

    try:
        from platform import window
        
        top_user_names = top_scores.keys()
        users_to_clear = []
        for i in range(window.localStorage.length):
            user_name = window.localStorage.key(i)
            if user_name not in top_user_names:
                users_to_clear.append(user_name)
                
        while users_to_clear: 
            window.localStorage.removeItem(users_to_clear.pop())
    finally:
        pass


def get_web_score_table():
    # converts scores dict to tables of strings to be rendered
    # Local storage version (web browser) or STUB
    
    shared.SCORE_TABLE = []
    if len(shared.SCORES) == 0:
        shared.SCORES = get_scores()
        
    rank = 0
    try:
        shared.SCORE_TABLE.append(["Rank", "Name", "Level", "Date"])
        for user_name, score in get_top_scores(shared.SCORES).items():
            rank += 1
            try:
                stored_timestamp = float(score["stored_timestamp"])
                ts = datetime.fromtimestamp(stored_timestamp).strftime("%Y-%m-%d %H:%M:%S")
            except:
                ts = "n/a"
            shared.SCORE_TABLE.append([str(rank), user_name, str(score["level"]), ts])
        if len(shared.SCORE_TABLE) == 1:
            shared.SCORE_TABLE = ["Highscore table is empty"]
    except Exception as e:
        shared.SCORE_TABLE = ["Highscore table temporally unavailable"]
        if shared.IS_DEBUG:
            shared.messages.append(f"Error in get_web_score_table")
            s = str(e)
            shared.messages += split_string(s, 30) 
        
        
def get_score_table():
    # gets scores using gamejoltapi and converts to tables of strings to be rendered
    # Game Jolt API version (desktop mode)
    
    if not shared.gamejoltapi:
        shared.SCORE_TABLE = ["Highscore table temporally unavailable"]
        return
    
    scores_payload = shared.gamejoltapi.scoresFetch(shared.NO_TOP_SCORES, shared.TEST_SCORE_TABLE_ID)
    shared.SCORE_TABLE = []
    if scores_payload["success"]:
        shared.SCORE_TABLE.append(["Rank", "Name", "Level", "Date"])
        for rank, score in enumerate(scores_payload["scores"]):
            ts = f"{datetime.fromtimestamp(score['stored_timestamp'])}"
            shared.SCORE_TABLE.append([str(rank+1), score["guest"], score["sort"], ts])
    else:
        shared.SCORE_TABLE = ["Highscore table temporally unavailable"]
        
        
async def get_score_table_async():
    # gets scores using gamejoltapi and converts to tables of strings to be rendered
    # WEB async version using Game Jolt API - NOT WORKING with pygbag
    
    # res = await _urlopen_async("https://postman-echo.com/delay/2")
    # print(res)
    # return

    # get top scores
    # print("gamejoltapi.scoresFetch")
    if not shared.gamejoltapi:
        shared.SCORE_TABLE = ["Highscore table temporally unavailable"]
        return

    scores_payload = await shared.gamejoltapi.scoresFetch(shared.NO_TOP_SCORES, shared.TEST_SCORE_TABLE_ID)
    # print(scores_payload)
    shared.SCORE_TABLE = []
    if scores_payload["success"]:
        shared.SCORE_TABLE.append(["Rank", "Name", "Level", "Date"])
        # print(scores_payload["scores"][0])
        for rank, score in enumerate(scores_payload["scores"]):
            ts = f"{datetime.fromtimestamp(score['stored_timestamp'])}"
            shared.SCORE_TABLE.append([str(rank+1), score["guest"], score["sort"], ts])
    else:
        shared.SCORE_TABLE = ["Highscore table temporally unavailable"]


def render_score_table(scr):
    # render highscore table with top results
    
    if shared.IS_WEB:
        get_web_score_table()
    else:
        get_score_table()
        # asyncio.run(get_score_table_async())
    columns_x = [50, 50 + 80, 50 + 80 + 200, 50 + 80 + 250+ 80, 50 + 80 + 250 + 80 + 240]
    rows_cnt = len(shared.SCORE_TABLE)
    font_size = 38

    if rows_cnt == 1:
        render_rows_of_text(scr, 50, 100, 38, shared.SCORE_TABLE)
    else:
        # black panel under score table
        pg.draw.rect(scr, "black", [25, 100 - 20, columns_x[4], (rows_cnt + 1) * font_size])
        
        ft = shared.fonts[font_size]
        for j, row in enumerate(shared.SCORE_TABLE):
            for i, x in enumerate(columns_x[:-1]):
                label = ft.render(row[i], True, "yellow", "black")
                scr.blit(label, (x, (100 + (j * font_size))))


# ----------------------------
#  legacy/old (that is:initially defined by tom/alex)
#  utility functions
# ----------------------------
def draw_all_mobs(scrref):
    player = pyv.find_by_archetype("player")[0]
    monsters = pyv.find_by_archetype("monster")
    av_i, av_j = player["position"]
    exit_ent = pyv.find_by_archetype("exit")[0]
    potions = pyv.find_by_archetype("potion")

    # draw the exit
    if shared.game_state["visibility_m"].get_val(*exit_ent["position"]) or shared.EXIT_VISIBLE:
        if shared.TILESET:
            # adhoc_exit_tile = shared.TILESET.image_by_rank(shared.EXIT_TILE_RANK)
            adhoc_exit_tile = shared.TILESET[f"{shared.EXIT_TILE_RANK}.png"]
        else:
            adhoc_exit_tile = shared.exit_tile
        scrref.blit(
            adhoc_exit_tile, (
                exit_ent["position"][0] * shared.CELL_SIDE,
                (exit_ent["position"][1] + 1) * shared.CELL_SIDE,
                shared.CELL_SIDE,
                shared.CELL_SIDE
            )
        )

    # draw all potions
    for potion in potions:
        if shared.game_state["visibility_m"].get_val(*potion["position"]) or shared.ALL_POTIONS_VISIBLE:
            # print("show potion")
            if potion["effect"] == "Heal":
                img_index = shared.HEAL_TILE_RANK if shared.ALL_POTIONS_VISIBLE else shared.UNKNOWN_TILE_RANK
                # scrref.blit(shared.TILESET.image_by_rank(783), (potion["position"][0] * shared.CELL_SIDE, potion["position"][1] * shared.CELL_SIDE, shared.CELL_SIDE, shared.CELL_SIDE))
            elif potion["effect"] == "Poison":
                img_index = shared.POISON_TILE_RANK if shared.ALL_POTIONS_VISIBLE else shared.UNKNOWN_TILE_RANK
            else:
                continue
            # adhoc_pot_tile = shared.TILESET.image_by_rank(img_index) if shared.TILESET else shared.pot_tile
            adhoc_pot_tile = shared.TILESET[f"{img_index}.png"] if shared.TILESET else shared.pot_tile
            scrref.blit(
                adhoc_pot_tile,
                (potion["position"][0] * shared.CELL_SIDE, (potion["position"][1] + 1) * shared.CELL_SIDE, shared.CELL_SIDE,
                 shared.CELL_SIDE))

    # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
    proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
    targx, targy = proj_function(av_i, av_j + 1)
    scrref.blit(shared.AVATAR, (targx, targy, shared.CELL_SIDE, shared.CELL_SIDE))

    # draw all enemies
    for monster in monsters:
        pos = monster["position"]
        # pos, t = enemy_info
        if shared.ALL_MONSTERS_VISIBLE or shared.game_state["visibility_m"].get_val(*pos):
            en_i, en_j = pos[0] * shared.CELL_SIDE, (pos[1] + 1) * shared.CELL_SIDE
            if shared.ALL_MONSTERS_PATH_VISIBLE:
                pg.draw.rect(scrref, monster["color"], (en_i, en_j, shared.CELL_SIDE, shared.CELL_SIDE))
                if len(monster["path"]) > 1:
                    delta_x = (monster["no"] // 4) * 8
                    delta_y = (int(monster["no"] % 4)) * 8
                    for path_pos in monster["path"][1:-1]:
                        pg.draw.rect(
                            scrref, monster["color"], (
                                (path_pos[0] * shared.CELL_SIDE) + 4 + delta_x,
                                ((path_pos[1] + 1) * shared.CELL_SIDE) + 4 + delta_y,
                                4, 4
                            )
                        )
            scrref.blit(shared.MONSTER, (en_i, en_j, shared.CELL_SIDE, shared.CELL_SIDE))


def player_push(directio):
    player = pyv.find_by_archetype("player")[0]
    # monsters = pyv.find_by_archetype("monster")  # TODO kick mob feat. here?
    if (player["position"][0], player["position"][1]) not in shared.walkable_cells:
        # print("kick")
        # shared.messages.append("Wall")
        deltas = {
            0: (+1, 0),
            1: (0, -1),
            2: (-1, 0),
            3: (0, +1)
        }
        player["position"][0] -= deltas[directio][0]
        player["position"][1] -= deltas[directio][1]
    # Update player vision
    world.update_vision_and_mobs(player["position"][0], player["position"][1])
