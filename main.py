import pygame
import random
from engine import *
from pygame import mixer
from lush import *
from models import Config

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


class Image:
    def __init__(self, path):
        self.image_show = fixed_resize_height(image.load('assets/halloween/' + path + '.png').convert_alpha(), 40)


class ImageList:
    def __init__(self, path_list):
        self.image_list = []
        self.load_all_images(path_list)
        self.actual_index = 0
        self.max_index = len(self.image_list) - 1

    def next_image(self):
        self.actual_index += 1
        if self.actual_index > self.max_index:
            self.actual_index = 0

    def get_actual_image(self):
        img = self.image_list[self.actual_index]
        self.next_image()
        return img.image_show

    def load_all_images(self, path_list):
        for path in path_list:
            self.image_list.append(Image(path))


class HeartImage:
    def __init__(self):
        self.images = ImageList(['l1', 'l2', 'l3', 'l4'])


class CoinImage:
    def __init__(self):
        self.images = ImageList(['p1', 'p2', 'p3', 'p4'])


class TatiskyGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Roletrando Tatisky")
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
        self.background = image.load('assets/halloween/img.png').convert_alpha()
        self.qrcode = image.load('assets/qr_code.png').convert_alpha()
        self.result_board = image.load('assets/board_last_result.png').convert_alpha()
        self.cron_board = image.load('assets/cron.png').convert_alpha()

        # self.heart_image = image.load('assets/heart.png').convert_alpha()
        # self.coins_image = image.load('assets/coins_gift.png').convert_alpha()

        self.heart_image = HeartImage()
        self.coins_image = CoinImage()

        self.podium_image = resize(image.load('assets/podio.png').convert_alpha(), 1.8)
        self.lush_image = image.load('assets/lush.png').convert_alpha()
        self.like_engine = Like()
        self.gift_engine = Gift()
        self.sub_engine = Subscribe()
        self.last_result_list = []
        # Criar setores com números
        self.current_angle = 0
        self.speed = 0
        self.spinning = False
        self.gift_image = resize(image.load('assets/coins.png').convert_alpha(), 0.08)
        self.like_image = resize(image.load('assets/likes.png').convert_alpha(), 0.15)
        self.sub_image = resize(image.load('assets/sub.png').convert_alpha(), 0.15)
        self.center_wheel = None
        self.border_wheel = image.load('assets/halloween/borda.png').convert_alpha()
        self.table = image.load('assets/tabela.png').convert_alpha()
        self.sup_line = image.load('assets/sup_line.png').convert_alpha()
        self.sup_line_spin = image.load('assets/sup_line_spin.png').convert_alpha()
        self.bottom_line = image.load('assets/botton_line.png').convert_alpha()
        self.sup_line_top_liker = resize(image.load('assets/sup_line_top_liker.png').convert_alpha(), 1.8)
        self.sup_line_top_gifter = resize(image.load('assets/sup_line_top_gifter.png').convert_alpha(), 1.8)
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
        self.start_key_1 = False
        self.start_key_2 = False
        self.start_key_3 = False
        self.start_key_4 = False
        self.start_key_5 = False
        self.start_key_6 = False
        self.start_key_7 = False
        self.start_key_8 = False
        mixer.init()
        self.wheel_sound = pygame.mixer.Sound('assets/click.mp3')
        self.end_time_song = pygame.mixer.Sound('assets/ding.mp3')
        self.sub_song = pygame.mixer.Sound('assets/sub.mp3')
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
        self.gradient_rect_podium(self.podium_image, (41, 694))
        name_position_list = [(265, 622), (118, 652), (405, 684)]
        points_position_list = [(265, 572), (118, 602), (405, 632)]
        image_position_list = [(220, 675), (73, 700), (365, 735)]
        self.screen.blit(self.podium_image, (320-88-191, 920-156))
        zip_to_blit = zip(self.like_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, (name_position[0] - rank_user.name.get_width()/2, name_position[1]))
            self.screen.blit(rank_user.points, (point_position[0] - rank_user.points.get_width()/2, point_position[1]))
            self.screen.blit(rank_user.image, image_position)
        self.screen.blit(self.sup_line_top_liker, (320-88-191, 490))

        self.gradient_rect_podium(self.podium_image, (1145, 694))
        self.screen.blit(self.podium_image, (1377-232, 920-156))
        zip_to_blit = zip(self.gift_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, ((name_position[0] - rank_user.name.get_width() / 2) + 1104, name_position[1]))
            self.screen.blit(rank_user.points, ((point_position[0] - rank_user.points.get_width()/2) + 1104, point_position[1]))
            self.screen.blit(rank_user.image, (image_position[0] + 1104, image_position[1]))
        self.screen.blit(self.sup_line_top_gifter, (1377-232, 490))

    def gradient_rect_podium(self, target_rect, position):
        colour_rect = pygame.Surface((2, 2)).convert_alpha()
        pygame.draw.line(colour_rect, AZUL, (0, 0), (0, 1))  # left colour line
        pygame.draw.line(colour_rect, VERDE, (1, 0), (1, 1))  # right colour line
        colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.get_width(), target_rect.get_height()+160))
        self.screen.blit(colour_rect, (position[0], position[1]-160))

    def draw_roulette(self):
        rotated_wheel = pygame.transform.rotate(self.next_spin.image_wheel, self.current_angle)
        wheel_rect = rotated_wheel.get_rect(center=self.background.get_rect().center)
        self.screen.blit(rotated_wheel, (wheel_rect[0]-88,wheel_rect[1] + 150))
        self.screen.blit(self.border_wheel, (655, 402))
        if self.subscriber_name_to_draw:
            self.draw_subscriber_name()

    def draw_subscriber_name(self):
        font = pygame.font.SysFont('Montserrat Heavy', 75, False)
        cost_surface = font.render(f'Roleta do {self.subscriber_name_to_draw}', True, WHITE)
        info_board_surface = pygame.Surface((cost_surface.get_width() + 100, 100), pygame.SRCALPHA).convert_alpha()
        info_board_surface.fill((255,0,0,100))
        position_sub_name = ((WIDTH/2 - cost_surface.get_width()/2) - 88, 920)
        position_info_board = ((WIDTH / 2 - info_board_surface.get_width() / 2) - 88, 920 - cost_surface.get_height()/2)
        position_sup_line = (WIDTH / 2 - self.sup_line.get_width()/2, position_info_board[Y_POSITION] - 30)
        position_bottom_line = (WIDTH / 2 - self.bottom_line.get_width()/2, position_info_board[Y_POSITION] + 80)
        self.gradient_rect(info_board_surface, position_info_board)
        self.screen.blit(self.sup_line, position_sup_line)
        self.screen.blit(self.bottom_line, position_bottom_line)
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

    def start(self):

        while not self.start_game:
            start_game = self.font_info.render('Aperte N para Jogo Novo ou C para carregar um jogo', True, RED)
            self.screen.blit(start_game, self.roleta_center)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        with open('spin.csv', 'w') as file:
                            file.write('0;0')
                            self.start_game = True
                    if event.key == pygame.K_c:
                        self.start_game = True
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
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.table, (1662, 152))
            self.like_engine.update(self)
            self.gift_engine.update(self)
            self.sub_engine.update(self)
            self.draw_last_result_board()
            # self.draw_qr_code()
            if self.transparent_time and self.is_start_cron:
                self.transparent_time_count()
            else:
                if self.is_start_cron:
                    self.end_time_song.play()
                self.is_start_cron = False
            if self.next_spin:
                self.mount_table()
                self.draw_roulette()
            self.draw_spin()
            self.get_next_spin()
            self.update()
            self.draw_podium()
            if self.word_game:
                if self.word_game.actual_word:
                    self.word_game.update(self)
                else:
                    self.word_game = None
            pygame.display.flip()
            if self.to_finish_angle:
                self.smooth_stop()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start_key_1 = True
                    if event.key == pygame.K_t:
                        self.start_key_2 = True
                    if event.key == pygame.K_1:
                        self.start_key_3 = True
                    if event.key == pygame.K_l:
                        self.start_key_4 = True
                    if event.key == pygame.K_j:
                        self.start_key_5 = True
                    if event.key == pygame.K_s:
                        self.start_key_6 = True

                    if event.key == pygame.K_r:
                        self.start_key_7 = True

                    if event.key == pygame.K_u:
                        self.start_key_8 = True

                    if self.start_key_1 and self.start_key_2:
                        self.is_start_cron = not self.is_start_cron
                    if self.start_key_1 and self.start_key_3:
                        self.like_engine.spin += 1
                    if self.start_key_1 and self.start_key_4:
                        self.change_lush_status()
                    if self.start_key_1 and self.start_key_5:
                        if self.word_game:
                            self.word_game.time_reveal = self.config.word_game_time_reveal
                            self.word_game.get_next_word()
                        else:
                            self.word_game = WordGame(self.config.word_game_time_reveal)
                            self.word_game.get_next_word()
                    if self.start_key_1 and self.start_key_6:
                        self.word_game.show_game = not self.word_game.show_game
                    if self.start_key_1 and self.start_key_7:
                        self.word_game.reveal()

                    if self.start_key_1 and self.start_key_8:
                        self.config = Config.select().get()
                        if self.word_game:
                            self.word_game.time_reveal = self.config.word_game_time_reveal
                        self.lush.lush_url = self.config.lush_url
                        self.lush.lush_api_key = self.config.lush_api_key

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.start_key_1 = False
                    if event.key == pygame.K_t:
                        self.start_key_2 = False
                    if event.key == pygame.K_1:
                        self.start_key_3 = False
                    if event.key == pygame.K_l:
                        self.start_key_4 = False

                    if event.key == pygame.K_j:
                        self.start_key_5 = False
                    if event.key == pygame.K_s:
                        self.start_key_6 = False
                    if event.key == pygame.K_r:
                        self.start_key_7 = False

                    if event.key == pygame.K_u:
                        self.start_key_8 = False

            if datetime.now() - self.result_countdown >= timedelta(milliseconds=5000):
                if self.next_spin:
                    if self.next_spin.spin and not self.spinning:
                        self.next_spin.table_results(self.get_last_result_list())
                        self.next_spin.spin -= 1
                        if self.gift_engine.lush_on:
                            self.lush.vibrate(1, self.lush.get_intense("Fraco"))
                        if self.next_spin.subscriber_name_list:
                            self.subscriber_name_to_draw = self.next_spin.subscriber_name_list.pop()
                            self.sub_song.play()
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
            self.screen.blit(self.lush_image, (1580, 30))

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
            new_heart = Heart(self.heart_image.images.get_actual_image(), randint(210, 660), randint(964, 1300))
            self.heart_list.append(new_heart)
            self.like_left_to_show -= 1

    def get_new_coins(self):
        while len(self.coins_list) < 10 and self.coins_left_to_show:
            new_coin = Coins(self.coins_image.images.get_actual_image(), randint(1228, 1666), randint(964, 1500))
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
        position_sup_line = ((WIDTH / 2 - self.sup_line_spin.get_width() / 2), position_info_board[Y_POSITION] - 30)
        position_bottom_line = ((WIDTH / 2 - self.bottom_line.get_width() / 2), position_info_board[Y_POSITION] + 80)
        self.gradient_rect(info_board_surface, position_info_board)
        self.screen.blit(self.sup_line_spin, position_sup_line)
        self.screen.blit(self.bottom_line, position_bottom_line)
        self.screen.blit(text_countdown, position_countdown)
        # self.screen.blit(cost_surface, (WIDTH/2, HEIGHT/2))

    def draw_spin(self):
        if self.spinning:
            if self.countdown:
                self.countdown_spin()
            else:
                current_sector = int(self.current_angle % 360 // self.angle_step)
                if current_sector != self.actual_sector:
                    self.wheel_sound.play()
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
        self.screen.blit(self.result_board, (0, 0))
        x = 728
        for type_value, dare in reversed(self.last_result_list):
            if type_value == 'coins':
                self.screen.blit(self.gift_image, (x, y - (61 * next_position)))
            elif type_value == 'subscribe':
                self.screen.blit(self.sub_image, (x, y - (61 * next_position)))
            else:
                self.screen.blit(self.like_image, (x, y - (61 * next_position)))

            cost_surface = self.font_info.render(dare.title, True, YELLOW)

            position_cost_text = (x + 55, y - (61 * next_position) + 10)
            self.screen.blit(cost_surface, position_cost_text)
            next_position += 1

        self.screen.blit(self.cron_board, (1743, 45))
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
        self.screen.blit(self.qrcode, (22, 462))


if __name__ == '__main__':
    game = TatiskyGame()
    game.start()

