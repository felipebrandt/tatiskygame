import pygame
import random
from engine import *
from pygame import mixer
from lush import *
from models import Config, ActionKey
from load_file import Assets
from hud_utils import Button


class ActionKeyMenu:
    def __init__(self, screen, action_keys, hot_key):
        self.screen = screen
        self.action_keys = action_keys
        self.hot_key = hot_key

        self.hot_key_image = resize(image.load('assets/long_button.png').convert_alpha(), 0.4)
        self.trigger_key_image = resize(image.load('assets/short_button.png').convert_alpha(), 0.4)

        self.width = 800
        self.height = 400
        self.x = (screen.get_width() - self.width) // 2
        self.hidden_y = -self.height
        self.visible_y = 50
        self.y = self.hidden_y

        self.content_surface = pygame.Surface((self.width - 40, self.height - 80))
        self.content_surface.set_colorkey((0, 0, 0))

        self.speed = 20
        self.is_open = False

        self.font_title = pygame.font.SysFont("arial", 26, bold=True)
        self.font = pygame.font.SysFont("arial", 18)
        self.key_font = pygame.font.SysFont("arial", 14, bold=True)
        self.desc_font = pygame.font.SysFont("arial", 18)

        self.bg_color = (25, 25, 25)
        self.border_color = (180, 180, 180)
        self.text_color = (255, 175, 195)

        self.scroll_offset = 0
        self.max_scroll = 0

    def toggle(self):
        self.is_open = not self.is_open

    def update(self):
        target_y = self.visible_y if self.is_open else self.hidden_y

        if self.y < target_y:
            self.y = min(self.y + self.speed, target_y)
        elif self.y > target_y:
            self.y = max(self.y - self.speed, target_y)

    def handle_event(self, event):
        if not self.is_open:
            return

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset += event.y * 30  # ajuste velocidade
            self.scroll_offset = max(
                min(self.scroll_offset, 0),
                -self.max_scroll
            )

    def draw(self):
        if self.y <= self.hidden_y:
            return

        # Painel externo
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 2, border_radius=8)

        # Título
        title = self.font_title.render("ATALHOS DISPONÍVEIS", True, self.text_color)
        self.screen.blit(title, (self.x + 20, self.y + 15))

        # 🔹 Limpa a surface interna
        self.content_surface.fill(self.bg_color)

        y_offset = self.scroll_offset
        content_height = 0

        hotkey_name = self.hot_key.name

        hotkey_surface = self.render_key(
            self.hot_key_image,
            hotkey_name,
            self.key_font,
            (255, 255, 255)
        )

        for trigger_key, action in self.action_keys.items():
            trigger_name = trigger_key

            trigger_surface = self.render_key(
                self.trigger_key_image,
                trigger_name,
                self.key_font,
                (255, 255, 255)
            )

            desc_text = f"{action.description}"
            desc_surface = self.desc_font.render(desc_text, True, self.text_color)

            # 🔹 altura da linha (mantendo sua lógica)
            item_height = max(
                hotkey_surface.get_height(),
                trigger_surface.get_height()
            ) + 12

            # 🔹 centro vertical da linha
            center_y = y_offset + item_height // 2

            # HOT KEY (centralizado)
            self.content_surface.blit(
                hotkey_surface,
                (0, center_y - hotkey_surface.get_height() // 2)
            )

            # "+"
            plus_text = self.desc_font.render("+", True, (255, 145, 165))
            self.content_surface.blit(
                plus_text,
                (
                    hotkey_surface.get_width() + 6,
                    center_y - plus_text.get_height() // 2
                )
            )

            # TRIGGER KEY (centralizado)
            x_trigger = hotkey_surface.get_width() + 20
            self.content_surface.blit(
                trigger_surface,
                (x_trigger, center_y - trigger_surface.get_height() // 2)
            )

            # DESCRIÇÃO (centralizada)
            desc_x = x_trigger + trigger_surface.get_width() + 20
            self.content_surface.blit(
                desc_surface,
                (desc_x, center_y - desc_surface.get_height() // 2)
            )

            y_offset += item_height
            content_height += item_height

        viewport_height = self.content_surface.get_height()
        self.max_scroll = max(0, content_height - viewport_height)

        self.screen.blit(
            self.content_surface,
            (self.x + 20, self.y + 60)
        )

    @staticmethod
    def render_key(surface, key_name, font, text_color=(20, 20, 20)):
        key_surface = surface.copy()

        text = font.render(key_name.upper(), True, text_color)
        text_rect = text.get_rect(center=key_surface.get_rect().center)

        key_surface.blit(text, text_rect)
        return key_surface

# Configurações iniciais
WIDTH, HEIGHT = 1980, 1024
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ROXO = (40, 0, 80, 120)
ROSA = (80, 0, 90, 120)
AZUL = (50, 50, 200, 120)
VERDE = (50, 200, 50, 120)
ROSA_CLARO = (100, 45, 65, 120)
RED = (255,0,0)
SMOOTH_VALUE = 0.2
SECTORS = 12
X_POSITION = 0
Y_POSITION = 1


class TatiskyGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Roletrando Tatisky")
        self.assets = None
        self.clock = pygame.time.Clock()
        self.font_info = pygame.font.SysFont('Montserrat Heavy', 25, False)
        self.font_counter = pygame.font.SysFont('Montserrat Heavy', 100, False)
        self.countdown = 0
        self.countdown_timer = datetime.now()
        self.zoom_countdown = 1
        self.result_countdown = datetime.now()
        # Configuração da roleta
        self.result = None
        self.angle_step = 360 / SECTORS
        self.roleta_center = (WIDTH // 2, HEIGHT // 2)
        self.radius = 200

        self.like_engine = Like()
        self.gift_engine = Gift()
        self.sub_engine = Subscribe()
        self.last_result_list = []
        # Criar setores com números
        self.current_angle = 0
        self.speed = 0
        self.spinning = False

        self.center_wheel = None

        self.regular_last_angle = None
        self.to_finish_angle = None
        self.running = False
        self.correction = 0
        self.next_spin = None
        self.actual_table_values = None
        self.actual_transparent_count = datetime.now()
        self.transparent_time = timedelta()
        self.bonus_time_transparent = timedelta(0)
        self.transparent_time_string = ''
        self.get_time_string()
        self.is_start_cron = False

        self.hot_key = None
        self.menu_key = None
        self.action_keys = {}
        self.action_menu = ActionKeyMenu(
            screen=self.screen,
            action_keys=self.action_keys,
            hot_key=self.hot_key
        )

        self.update_action_keys()
        self.theme_chose = False
        mixer.init()
        self.hud_button_images = {'frame_button': resize(image.load('assets/frame_button.png'), 0.6),
                                  'button': resize(image.load('assets/button.png'), 0.6)}
        self.hud_window = image.load('assets/start_page.png')
        self.actual_sector = 0
        self.start_game = False
        self.subscriber_name_to_draw = None
        self.all_new_subscribers = []
        self.heart_list = []
        self.like_left_to_show = 0
        self.coins_list = []
        self.coins_left_to_show = 0
        self.like_rank = Ranking('liker')
        self.gift_rank = Ranking('gifter')
        self.word_game = None
        self.config = Config.select().get()
        self.lush = Lush(self.config)
        self.border_wheel_position = None

    def get_time_string(self):
        minute = self.transparent_time.seconds // 60
        second = self.transparent_time.seconds % 60
        minute_string = str(minute)
        if len(minute_string) == 1:
            minute_string = '0' + minute_string

        second_string = str(second)
        if len(second_string) == 1:
            second_string = '0' + second_string

        self.transparent_time_string = f'{minute_string if minute else "00"}:{second_string if second else "00"}'

    def mount_table(self):
        self.actual_table_values = self.next_spin.table
        y = 195
        next_position = 0
        for dare in self.actual_table_values:
            if next_position == 12:
                break
            if self.result is not None and next_position == self.result:
                cost_surface = self.font_info.render(dare.title,
                                                     True,
                                                     YELLOW)
            else:
                cost_surface = self.font_info.render(dare.title,
                                                     True,
                                                     WHITE)

            position_cost_text = (1760, y + (61 * next_position))
            self.screen.blit(cost_surface, position_cost_text)
            next_position += 1

    def draw_podium(self):
        self.gradient_rect_podium(self.assets.podium_image, (41, 694))
        name_position_list = [(265, 622), (118, 652), (405, 684)]
        points_position_list = [(265, 572), (118, 602), (405, 632)]
        image_position_list = [(220, 675), (73, 700), (365, 735)]
        self.screen.blit(self.assets.podium_image, (320-88-191, 920-156))
        zip_to_blit = zip(self.like_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, (name_position[0] - rank_user.name.get_width()/2, name_position[1]))
            self.screen.blit(rank_user.points, (point_position[0] - rank_user.points.get_width()/2, point_position[1]))
            self.screen.blit(rank_user.image, image_position)
        self.screen.blit(self.assets.sup_line_top_liker, (320-88-191, 490))

        self.gradient_rect_podium(self.assets.podium_image, (1145, 694))
        self.screen.blit(self.assets.podium_image, (1377-232, 920-156))
        zip_to_blit = zip(self.gift_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, ((name_position[0] - rank_user.name.get_width() / 2) + 1104, name_position[1]))
            self.screen.blit(rank_user.points, ((point_position[0] - rank_user.points.get_width()/2) + 1104, point_position[1]))
            self.screen.blit(rank_user.image, (image_position[0] + 1104, image_position[1]))
        self.screen.blit(self.assets.sup_line_top_gifter, (1377-232, 490))

    def gradient_rect_podium(self, target_rect, position):
        colour_rect = pygame.Surface((2, 2)).convert_alpha()
        pygame.draw.line(colour_rect, AZUL, (0, 0), (0, 1))  # left colour line
        pygame.draw.line(colour_rect, VERDE, (1, 0), (1, 1))  # right colour line
        colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.get_width(), target_rect.get_height()+160))
        self.screen.blit(colour_rect, (position[0], position[1]-160))

    def draw_roulette(self):
        rotated_wheel = pygame.transform.rotate(self.next_spin.image_wheel, self.current_angle)
        wheel_rect = rotated_wheel.get_rect(center=self.assets.background.get_rect().center)
        self.screen.blit(rotated_wheel, (wheel_rect[0]-88,wheel_rect[1] + 150))
        self.screen.blit(self.assets.border_wheel, self.border_wheel_position)
        if self.subscriber_name_to_draw:
            self.draw_subscriber_name()

    def draw_subscriber_name(self):
        font = pygame.font.SysFont('Montserrat Heavy', 75, False)
        cost_surface = font.render(f'Roleta do {self.subscriber_name_to_draw}', True, WHITE)
        info_board_surface = pygame.Surface((cost_surface.get_width() + 100, 100), pygame.SRCALPHA).convert_alpha()
        info_board_surface.fill((255,0,0,100))
        position_sub_name = ((WIDTH/2 - cost_surface.get_width()/2) - 88, 920)
        position_info_board = ((WIDTH / 2 - info_board_surface.get_width() / 2) - 88, 920 - cost_surface.get_height()/2)
        position_sup_line = (WIDTH / 2 - self.assets.sup_line.get_width()/2, position_info_board[Y_POSITION] - 30)
        position_bottom_line = (WIDTH / 2 - self.assets.bottom_line.get_width()/2, position_info_board[Y_POSITION] + 80)
        self.gradient_rect(info_board_surface, position_info_board)
        self.screen.blit(self.assets.sup_line, position_sup_line)
        self.screen.blit(self.assets.bottom_line, position_bottom_line)
        self.screen.blit(cost_surface, position_sub_name)

    def gradient_rect(self, target_rect, position):
        """ Draw a horizontal-gradient filled rectangle covering <target_rect> """
        colour_rect = pygame.Surface((2, 2)).convert_alpha()
        pygame.draw.line(colour_rect, ROXO, (0, 0), (0, 1))  # left colour line
        pygame.draw.line(colour_rect, ROSA, (1, 0), (1, 1))  # right colour line
        colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.get_width(), target_rect.get_height()))
        self.screen.blit(colour_rect, position)

    def smooth_stop(self):
        self.current_angle = int(self.current_angle * 100)/100

        if (self.current_angle > self.to_finish_angle) and self.correction == 1:
            self.current_angle = self.to_finish_angle

        if (self.current_angle < self.to_finish_angle) and self.correction == -1:
            self.current_angle = self.to_finish_angle

        if self.current_angle != self.to_finish_angle:
            self.current_angle += self.correction * SMOOTH_VALUE
        else:
            self.regular_last_angle = None
            self.to_finish_angle = None

    def blit(self, image_blit, position):
        self.screen.blit(image_blit, position)

    def start(self):
        theme = ''
        button_theme_a = Button(self.hud_button_images, 'Normal')
        button_theme_b = Button(self.hud_button_images, 'Halloween')
        button_theme_c = Button(self.hud_button_images, 'Natal')
        button_theme_d = Button(self.hud_button_images, 'Ano Novo')
        button_theme_e = Button(self.hud_button_images, 'Férias')
        button_theme_f = Button(self.hud_button_images, 'Carnaval')
        button_start = Button(self.hud_button_images, 'Iniciar')
        while not self.start_game:
            self.blit(self.hud_window, (0, 0))

            if self.theme_chose:
                start_game = self.font_counter.render('Inicie o Jogo!', True, WHITE)
            else:
                start_game = self.font_counter.render('Escolha o Tema da LIVE', True, WHITE)

            self.screen.blit(start_game, ((WIDTH // 2) - (start_game.get_width() // 2), 360))
            if not self.theme_chose:
                button_theme_a.update(self, 770, 470)
                button_theme_b.update(self, 1050, 470)
                button_theme_c.update(self, 770, 600)
                button_theme_d.update(self, 1050, 600)
                button_theme_e.update(self, 770, 730)
                button_theme_f.update(self, 1050, 730)

            if self.theme_chose:
                button_start.update(self, (WIDTH // 2) - (button_start.frame_button.get_width() // 2), 470)

            if button_theme_a.end_animation:
                self.theme_chose = True
                theme = 'normal'
                self.border_wheel_position = (664, 445)

            if button_theme_b.end_animation:
                self.theme_chose = True
                theme = 'halloween'
                self.border_wheel_position = (655, 402)

            if button_theme_c.end_animation:
                self.theme_chose = True
                theme = 'natal'
                self.border_wheel_position = (691, 408)

            if button_theme_d.end_animation:
                self.theme_chose = True
                theme = 'ano_novo'
                self.border_wheel_position = (680, 375)

            if button_theme_e.end_animation:
                self.theme_chose = True
                theme = 'ferias'
                self.border_wheel_position = (646, 409)

            if button_theme_f.end_animation:
                self.theme_chose = True
                theme = 'carnaval'
                self.border_wheel_position = (638, 413)

            if button_start.end_animation:
                self.start_game = True
                self.blit(self.hud_window, (0, 0))
                load_game = self.font_counter.render('CARREGANDO O JOGO...', True, WHITE)
                self.screen.blit(load_game, ((WIDTH // 2) - (load_game.get_width() // 2), 360))
                with open('spin.csv', 'w') as file:
                    file.write('0;0')

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # elif event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_n:
                #         with open('spin.csv', 'w') as file:
                #             file.write('0;0')
                #             self.start_game = True
                #     if event.key == pygame.K_c:
                #         self.start_game = True
        self.assets = Assets(theme)
        self.like_engine.update(self)
        self.gift_engine.update(self)
        self.sub_engine.update(self)
        self.gift_engine.start_spin()
        self.like_engine.start_spin()
        self.sub_engine.start_spin()
        while not self.running:
            if not self.like_engine.validate_extract():
                start_tki = self.font_info.render('Inicie o TKI', True, RED)
                self.screen.blit(start_tki, self.roleta_center)
                pygame.display.flip()
            else:
                self.running = True

        while self.running:
            self.screen.blit(self.assets.background, (0, 0))
            self.screen.blit(self.assets.table, (1662, 152))
            self.like_engine.update(self)
            self.gift_engine.update(self)
            self.sub_engine.update(self)
            self.draw_last_result_board()
            # self.draw_qr_code()
            if self.transparent_time and self.is_start_cron:
                self.transparent_time_count()
            else:
                if self.is_start_cron:
                    self.assets.end_time_song.play()
                self.is_start_cron = False
            if self.next_spin:
                self.mount_table()
                self.draw_roulette()
            self.draw_spin()
            self.get_next_spin()
            self.update()
            self.draw_podium()

            self.action_menu.update()
            self.action_menu.draw()

            if self.word_game:
                if self.word_game.actual_word:
                    self.word_game.update(self)
                else:
                    self.word_game = None
            pygame.display.flip()
            if self.to_finish_angle:
                self.smooth_stop()
            for event in pygame.event.get():
                self.action_menu.handle_event(event)

                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if pygame.key.name(event.key) == self.hot_key.trigger_key:
                        self.hot_key.is_active = True
                    if pygame.key.name(event.key) == self.menu_key.trigger_key:
                        self.menu_key.is_active = True
                    if self.action_keys.get(pygame.key.name(event.key)):
                        self.action_keys[pygame.key.name(event.key)].is_active = True

                    if self.menu_key.is_active:
                        self.menu_key.execute_action(self)

                    if self.hot_key.is_active:
                        for action_key in self.action_keys.values():
                            if action_key.is_active:
                                action_key.execute_action(self)
                                break

                elif event.type == pygame.KEYUP:
                    if pygame.key.name(event.key) == self.hot_key.trigger_key:
                        self.hot_key.is_active = False
                    if pygame.key.name(event.key) == self.menu_key.trigger_key:
                        self.menu_key.is_active = False
                    if self.action_keys.get(pygame.key.name(event.key)):
                        self.action_keys[pygame.key.name(event.key)].is_active = False

            if datetime.now() - self.result_countdown >= timedelta(milliseconds=5000):
                if self.next_spin:
                    if self.next_spin.spin and not self.spinning:
                        self.next_spin.table_results(self.get_last_result_list())
                        self.next_spin.spin -= 1
                        if self.gift_engine.lush_on:
                            self.lush.vibrate(1, self.lush.get_intense("Fraco"))
                        if self.next_spin.subscriber_name_list:
                            self.subscriber_name_to_draw = self.next_spin.subscriber_name_list.pop()
                            self.assets.sub_song.play()
                        else:
                            self.subscriber_name_to_draw = None
                        self.next_spin.all_spinning += 1
                        self.speed = random.randint(150, 300)
                        self.countdown_timer = datetime.now()
                        self.countdown = 3
                        self.zoom_countdown = 1
                        self.spinning = True
                        self.result = None
                    if not self.next_spin.spin and not self.spinning:
                        self.next_spin = None

            self.clock.tick(30)

        pygame.quit()

    def change_lush_status(self):
        self.gift_engine.lush_on = not self.gift_engine.lush_on
        self.like_engine.lush_on = not self.like_engine.lush_on

    def update(self):
        self.like_rank.update()
        self.gift_rank.update()
        self.get_new_hearts()
        self.get_new_coins()
        self.lush_update()
        for heart in self.heart_list:
            heart.update(self)
        for coin in self.coins_list:
            coin.update(self)
        self.validate_all_hearts()
        self.validate_all_coins()

    def lush_update(self):
        if self.gift_engine.lush_on:
            self.screen.blit(self.assets.lush_image, (1580, 30))

    def validate_all_hearts(self):
        remove = False
        next_index = 0
        while not remove and next_index < len(self.heart_list):
            if not self.heart_list[next_index].is_valid:
                self.heart_list.pop(next_index)
                remove = True
            next_index += 1

    def validate_all_coins(self):
        remove = False
        next_index = 0
        while not remove and next_index < len(self.coins_list):
            if not self.coins_list[next_index].is_valid:
                self.coins_list.pop(next_index)
                remove = True
            next_index += 1

    def get_new_hearts(self):
        while len(self.heart_list) < 50 and self.like_left_to_show:
            new_heart = Heart(self.assets.heart_image.images.get_actual_image(), randint(210, 660), randint(964, 1300))
            self.heart_list.append(new_heart)
            self.like_left_to_show -= 1

    def get_new_coins(self):
        while len(self.coins_list) < 10 and self.coins_left_to_show:
            new_coin = Coins(self.assets.coins_image.images.get_actual_image(), randint(1228, 1666), randint(964, 1500))
            self.coins_list.append(new_coin)
            self.coins_left_to_show -= 1

    def get_next_spin(self):
        if self.next_spin is None:
            if self.sub_engine.spin:
                self.next_spin = self.sub_engine
            elif self.gift_engine.spin:
                self.next_spin = self.gift_engine
            elif self.like_engine.spin:
                self.next_spin = self.like_engine

    def get_last_result_list(self):
        result_list = []
        for result_type, result in self.last_result_list:
            if result_type == 'like':
                if result:
                    result_list.append(result)
            elif result_type == 'coin':
                if result:
                    result_list.append(result)
            else:
                if result:
                    result_list.append(result)

        return result_list

    def countdown_spin(self):
        if datetime.now() - self.countdown_timer <= timedelta(milliseconds=1500):
            text_countdown = self.font_counter.render('               ' + str(self.countdown) + '               ', True,
                                                      WHITE)
        else:
            self.countdown -= 1
            self.countdown_timer = datetime.now()
            text_countdown = self.font_counter.render('               ' + str(self.countdown) + '               ', True,
                                                      WHITE)

        info_board_surface = pygame.Surface((text_countdown.get_width() + 100, 100), pygame.SRCALPHA).convert_alpha()
        info_board_surface.fill((255, 0, 0, 100))
        position_countdown = ((WIDTH / 2 - text_countdown.get_width() / 2), 50)
        position_info_board = ((WIDTH / 2 - info_board_surface.get_width() / 2) - 12, (320 - text_countdown.get_height() / 2) - 262)
        position_sup_line = ((WIDTH / 2 - self.assets.sup_line_spin.get_width() / 2), position_info_board[Y_POSITION] - 30)
        position_bottom_line = ((WIDTH / 2 - self.assets.bottom_line.get_width() / 2), position_info_board[Y_POSITION] + 80)
        self.gradient_rect(info_board_surface, position_info_board)
        self.screen.blit(self.assets.sup_line_spin, position_sup_line)
        self.screen.blit(self.assets.bottom_line, position_bottom_line)
        self.screen.blit(text_countdown, position_countdown)
        # self.screen.blit(cost_surface, (WIDTH/2, HEIGHT/2))

    def draw_spin(self):
        if self.spinning:
            if self.countdown:
                self.countdown_spin()
            else:
                current_sector = int(self.current_angle % 360 // self.angle_step)
                if current_sector != self.actual_sector:
                    self.assets.wheel_sound.play()
                    self.actual_sector = current_sector
                self.current_angle += self.speed
                self.speed *= 0.98  # Reduz a velocidade gradativamente
                if self.speed < 0.1:
                    self.spinning = False
                    self.speed = 0
                    self.regular_last_angle = self.current_angle % 360 // 1
                    self.to_finish_angle = (self.current_angle % 360 // self.angle_step) * 30 + 15
                    self.current_angle = self.regular_last_angle
                    if self.current_angle > self.to_finish_angle:
                        self.correction = -1
                    else:
                        self.correction = 1
                    self.result = int(self.current_angle % 360 // self.angle_step)
                    if len(self.last_result_list) == 4:
                        self.last_result_list.pop(0)
                    self.last_result_list.append((self.next_spin.table_type, self.actual_table_values[self.result]))
                    with open('spin.csv', 'w') as file:
                        file.write(f'{self.gift_engine.all_spinning};{self.like_engine.all_spinning}')
                    self.result_countdown = datetime.now()
                    self.verify_result(self.actual_table_values[self.result])

    def draw_last_result_board(self):
        y = 338
        next_position = 0
        self.screen.blit(self.assets.result_board, (0, 0))
        x = 728
        for type_value, dare in reversed(self.last_result_list):
            if type_value == 'coins':
                self.screen.blit(self.assets.gift_image, (x, y - (61 * next_position)))
            elif type_value == 'subscribe':
                self.screen.blit(self.assets.sub_image, (x, y - (61 * next_position)))
            else:
                self.screen.blit(self.assets.like_image, (x, y - (61 * next_position)))

            cost_surface = self.font_info.render(dare.title, True, YELLOW)

            position_cost_text = (x + 55, y - (61 * next_position) + 10)
            self.screen.blit(cost_surface, position_cost_text)
            next_position += 1

        self.screen.blit(self.assets.cron_board, (1743, 45))
        self.get_time_string()
        if self.is_start_cron:
            cost_surface = self.font_info.render(self.transparent_time_string, True, WHITE)
        else:
            cost_surface = self.font_info.render(self.transparent_time_string, True, RED)
        cost_surface = resize(cost_surface, 3)
        position_cost_text = (1751, 56)
        self.screen.blit(cost_surface, position_cost_text)

    def transparent_time_count(self):
        if datetime.now() - self.actual_transparent_count > timedelta(seconds=1):
            self.transparent_time -= timedelta(seconds=1)
            self.actual_transparent_count = datetime.now()

    def plus_chron(self, plus_value: timedelta):
        self.actual_transparent_count = datetime.now()
        self.transparent_time += plus_value

    def verify_result(self, dare: Dare):
        for minutes in range(10):
            if f'+ {minutes} Min' in dare.title:
                self.plus_chron(timedelta(minutes=dare.value))
        if 'Vibra' in dare.title:
            action, intense, trash, time_sec, time_trash = dare.title.split(' ')
            self.lush.vibrate(int(dare.value), self.lush.get_intense(intense))

    def draw_qr_code(self):
        self.screen.blit(self.assets.qrcode, (22, 462))

    def clear_spins(self):
        self.gift_engine.spin = 0
        self.like_engine.spin = 0

    def update_action_keys(self):
        action_keys = {}
        for action_key in ActionKey.select().where(ActionKey.is_valid == True and ActionKey.is_hot_key == False):
            action_keys[action_key.trigger_key] = action_key
        self.hot_key = ActionKey.select().where(ActionKey.name == 'crtl').get()
        self.menu_key = ActionKey.select().where(ActionKey.name == 'Menu').get()
        self.action_keys = action_keys
        self.action_menu.action_keys = action_keys
        self.action_menu.hot_key = self.hot_key


if __name__ == '__main__':
    game = TatiskyGame()
    game.start()

