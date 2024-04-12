from . import pimodules
from . import shared


pg = pimodules.pyved_engine.pygame


class InputBox:
    # https://stackoverflow.com/questions/46390231/how-can-i-create-a-text-input-box-with-pygame
    def __init__(self, x, y, w, h, text='', max_len=0):
        self.rect = pg.Rect(x, y, w, h)
        self.color = shared.COLOR_ACTIVE
        self.max_len = max_len
        self.text = text[:self.max_len] if self.max_len else text
        self.ft = shared.fonts[24]
        self.active = True
        self.txt_surface = None  # self.ft.render(f"{self.text}", True, self.color, "black") # FONT.render(text, True, self.color)
        self.render_text()

    def render_text(self):
        suffix = "_" if self.active else ""
        self.txt_surface = self.ft.render(f"{self.text}{suffix}", True, self.color,
                                          "black")  # FONT.render(self.text, True, self.color)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = shared.COLOR_ACTIVE if self.active else shared.COLOR_INACTIVE
            self.render_text()
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_ESCAPE:
                    # self.active = False
                    # self.color = shared.COLOR_ACTIVE if self.active else shared.COLOR_INACTIVE
                    # self.render_text()
                    shared.show_input = False
                elif event.key == pg.K_RETURN:
                    # print(self.text)
                    shared.user_name = self.text
                    shared.show_input = False
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key not in [pg.K_TAB]:
                    self.text += event.unicode
                    self.text = self.text[:self.max_len] if self.max_len else self.text
                # Re-render the text.
                # suffix = "_" if self.active else ""
                # self.txt_surface = self.ft.render(f"{self.text}{suffix}", True, self.color, "black") # FONT.render(self.text, True, self.color)
                self.render_text()

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        pg.draw.rect(screen, 'black', self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)
