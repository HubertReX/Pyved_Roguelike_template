import random
from . import shared
from . import pimodules
# from pygame_menu.examples import create_example_window

pyv = pimodules.pyved_engine
pyv.bootstrap_e()
pygame = pyv.pygame

# from . import gamejoltapi
# import gamejoltapi

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

Spritesheet = pyv.gfx.Spritesheet


def start_game():
    shared.user_name = shared.user_name_input.get_value()
    shared.show_input = False
    shared.menu.disable()

class InputBox:
    # https://stackoverflow.com/questions/46390231/how-can-i-create-a-text-input-box-with-pygame
    def __init__(self, x, y, w, h, text='', max_len=0):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = shared.COLOR_ACTIVE
        self.max_len = max_len
        self.text = text[:self.max_len] if self.max_len else text
        self.ft = shared.fonts[24]
        self.active = True
        self.txt_surface = None #self.ft.render(f"{self.text}", True, self.color, "black") # FONT.render(text, True, self.color)
        self.render_text()

    def render_text(self):
        suffix = "_" if self.active else ""
        self.txt_surface = self.ft.render(f"{self.text}{suffix}", True, self.color, "black") # FONT.render(self.text, True, self.color)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = shared.COLOR_ACTIVE if self.active else shared.COLOR_INACTIVE
            self.render_text()
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_ESCAPE:
                    # self.active = False
                    # self.color = shared.COLOR_ACTIVE if self.active else shared.COLOR_INACTIVE
                    # self.render_text()
                    shared.show_input = False
                elif event.key == pygame.K_RETURN:
                    # print(self.text)
                    shared.user_name = self.text
                    shared.show_input = False
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key not in [pygame.K_TAB]:
                    self.text += event.unicode
                    self.text = self.text[:self.max_len] if self.max_len else self.text
                # Re-render the text.
                # suffix = "_" if self.active else ""
                # self.txt_surface = self.ft.render(f"{self.text}{suffix}", True, self.color, "black") # FONT.render(self.text, True, self.color)
                self.render_text()
                
    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        pygame.draw.rect(screen, 'black', self.rect)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

def load_fonts():
    font_sizes = [24, 38]
    for font_size in font_sizes:
        shared.fonts[font_size] = pyv.pygame.font.Font(None, font_size)
    
def init_menu():
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
    
    # shared.gamejoltapi = gamejoltapi.GameJoltAPI(
    #     shared.GAME_ID,
    #     shared.PRIVATE_KEY,
    #     # username=USERNAME,
    #     # userToken=TOKEN,
    #     responseFormat="json",
    #     submitRequests=True
    # )    
    shared.user_name_input = InputBox(135, 205, 140, 32, max_len=10)
    
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
    pyv.init_entity(monster, {
        'position': position,
        'damages': shared.MONSTER_DMG,
        'health_point': shared.MONSTER_HP,
        'no': no,
        'color': (random.randint(20,255), random.randint(20,255), random.randint(20,255)),
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


def init_images():
    grid_rez = (32, 32)

    img = pyv.vars.images['tileset']
    tileset = Spritesheet(img, 2)  # use upscaling x2
    tileset.set_infos(grid_rez)

    img = pyv.vars.images['avatar1']
    planche_avatar = Spritesheet(img, 2)  # upscaling x2
    planche_avatar.set_infos(grid_rez)
    planche_avatar.colorkey = (255, 0, 255)

    monster_img = pyv.vars.images['monster']
    monster_img = pygame.transform.scale(monster_img, (32, 32))
    monster_img.set_colorkey((255, 0, 255))
    shared.AVATAR = planche_avatar.image_by_rank(0)
    shared.TILESET = tileset
    shared.MONSTER = monster_img


def can_see(cell):
    # print( shared.game_state['visibility_m'])
    return shared.game_state['visibility_m'].get_val(*cell)


def get_all_walkable_cells():
    w, h = 24, 24  # Update these dimensions to match your map size
    walkable_cells = []

    for i in range(w):
        for j in range(h):
            cell = (i, j)
            walkable_cells.append(cell)

    return walkable_cells
