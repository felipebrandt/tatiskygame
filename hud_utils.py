from pygame import Surface, mouse, font
from pygame.locals import *
import gc
from datetime import datetime, timedelta


class Button:
    def __init__(self, button_image, label):
        self.label = label
        self.frame_button = button_image['frame_button']
        self.button = button_image['button']
        self.down_button = Surface.copy(self.button)
        self.brightness = 80
        self.down_button.fill((self.brightness, self.brightness, self.brightness), special_flags=BLEND_RGB_ADD)
        self.rect_frame = self.frame_button.get_rect()
        self.rect_button = self.button.get_rect()
        self.width, self.height = self.button.get_size()
        self.is_pressed = False
        self.end_animation = False
        self.frame_image = 0
        self.actual_button = self.button
        self.return_state_time = datetime.now()

    def clear(self):
        self.is_pressed = False
        self.end_animation = False
        self.frame_image = 0
        self.actual_button = self.button

    def set_position(self, position_x, position_y):
        self.rect_button.topleft = (position_x, position_y)
        self.rect_frame.topleft = (position_x, position_y)

    def update(self, game, position_x, position_y):
        self.set_position(position_x, position_y)
        self.collision()
        if self.frame_image > 1:
            self.actual_button = self.button
            self.end_animation = True
        game.blit(self.frame_button, self.rect_frame)
        game.blit(self.actual_button, self.rect_button)
        if self.is_pressed:
            self.actual_button = self.down_button
            if not self.end_animation:
                self.frame_image += 1
                self.return_state_time = datetime.now()
        font_button = font.SysFont('Montserrat Heavy', 30)
        button_string = font_button.render(self.label, False, (255, 255, 255))
        rect_back_string = button_string.get_rect(center=self.rect_button.center)
        game.blit(button_string, rect_back_string)
        if self.end_animation:
            if datetime.now() - self.return_state_time > timedelta(seconds=0.3):
                self.clear()

    def collision(self):
        if self.rect_button:
            mouse_x, mouse_y = mouse.get_pos()
            if (self.rect_button.left <= mouse_x <= self.rect_button.right) and\
                    (self.rect_button.top <= mouse_y <= self.rect_button.bottom):

                key_pressed = mouse.get_pressed()

                if key_pressed[0]:
                    self.is_pressed = True
                    gc.collect()


