import pygame.font


class Button:
    '''A class to create buttons for the game'''

    def __init__(self, ai_game, msg, button_color=(0, 135, 0), text_color=(255, 255, 255)) -> None:
        '''Initialize button attributes'''
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Set the dimensions and properties of the button
        self.width, self.height = 200, 50
        self.button_color = button_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 48)

        # Build the button's rect object and center it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # The button message needs to be prepped only once
        self.msg = msg
        self._prep_msg()

    def _prep_msg(self):
        '''Turn msg into a rendered image and center text on the button'''
        self.msg_image = self.font.render(self.msg, True, self.text_color,
                                          self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def set_position(self, x, y):
        '''Set the position of the button'''
        self.rect.x = x
        self.rect.y = y
        self.msg_image_rect.center = self.rect.center
    
    def set_color(self, color):
        '''Set the color of the button'''
        self.button_color = color
        self._prep_msg()

    def draw_button(self):
        '''Draw blank button and then draw message'''
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)
