import pygame
import random
import math
from pygame import image
from image_utils import *
from engine import *
from pygame import mixer

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
        pygame.display.set_caption("Roleta")
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
        self.background = image.load('assets/img.png').convert_alpha()
        self.qrcode = image.load('assets/qr_code.png').convert_alpha()
        self.result_board = image.load('assets/board_last_result.png').convert_alpha()
        self.cron_board = image.load('assets/cron.png').convert_alpha()
        self.heart_image = image.load('assets/heart.png').convert_alpha()
        self.coins_image = image.load('assets/coins_gift.png').convert_alpha()
        self.podium_image = image.load('assets/podio.png').convert_alpha()
        self.like_engine = Like()
        self.gift_engine = Gift()
        self.last_result_list = []
        # Criar setores com números
        self.current_angle = 0
        self.speed = 0
        self.spinning = False
        self.gift_image = resize(image.load('assets/coins.png').convert_alpha(), 0.08)
        self.like_image = resize(image.load('assets/likes.png').convert_alpha(), 0.12)
        self.center_wheel = None
        self.border_wheel = image.load('assets/borda.png').convert_alpha()
        self.flanelinha = image.load('assets/flanelinha.png').convert_alpha()
        self.table = image.load('assets/tabela.png').convert_alpha()
        self.sup_line = image.load('assets/sup_line.png').convert_alpha()
        self.sup_line_spin = image.load('assets/sup_line_spin.png').convert_alpha()
        self.bottom_line = image.load('assets/botton_line.png').convert_alpha()
        self.sup_line_top_liker = image.load('assets/sup_line_top_liker.png').convert_alpha()
        self.sup_line_top_gifter = image.load('assets/sup_line_top_gifter.png').convert_alpha()
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
        for value in self.actual_table_values:
            if next_position == 12:
                break
            if self.result is not None and next_position == self.result:
                cost_surface = self.font_info.render(value,
                                                     True,
                                                     YELLOW)
            else:
                cost_surface = self.font_info.render(value,
                                                     True,
                                                     WHITE)

            position_cost_text = (1760, y + (61 * next_position))
            self.screen.blit(cost_surface, position_cost_text)
            next_position += 1

    def draw_podium(self):
        self.gradient_rect_podium(self.podium_image, (320-88, 920))
        name_position_list = [(446-88, 841), (368-88, 865), (524-88, 876)]
        points_position_list = [(420-88, 800), (320-88, 800), (500-88, 800)]
        image_position_list = [(418-88, 870), (335-88, 890), (501-88, 902)]
        self.screen.blit(self.podium_image, (320-88, 920))
        zip_to_blit = zip(self.like_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, (name_position[0] - rank_user.name.get_width()/2,name_position[1]))
            self.screen.blit(rank_user.points, point_position)
            self.screen.blit(rank_user.image, image_position)
        self.screen.blit(self.sup_line_top_liker, (320-88, 730))

        self.gradient_rect_podium(self.podium_image, (1377, 920))
        name_position_list = [(446+1057, 841), (368+1057, 865), (524+1057, 876)]
        points_position_list = [(420+1057, 800), (320+1057, 800), (500+1057, 800)]
        image_position_list = [(418+1057, 870), (335+1057, 890), (501+1057, 902)]
        self.screen.blit(self.podium_image, (1377, 920))
        zip_to_blit = zip(self.gift_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, (name_position[0] - rank_user.name.get_width() / 2, name_position[1]))
            self.screen.blit(rank_user.points, point_position)
            self.screen.blit(rank_user.image, image_position)
        self.screen.blit(self.sup_line_top_gifter, (1377, 730))

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
        self.screen.blit(self.border_wheel, (664, 445))
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
        self.gift_engine.start_spin()
        self.like_engine.start_spin()
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

                    if self.start_key_1 and self.start_key_2:
                        self.is_start_cron = not self.is_start_cron

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.start_key_1 = False
                    if event.key == pygame.K_t:
                        self.start_key_2 = False

            if datetime.now() - self.result_countdown >= timedelta(milliseconds=5000):
                if self.next_spin:
                    if self.next_spin.spin and not self.spinning:
                        self.next_spin.spin -= 1
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

    def update(self):
        self.like_rank.update()
        self.gift_rank.update()
        self.get_new_hearts()
        self.get_new_coins()
        for heart in self.heart_list:
            heart.update(self)
        for coin in self.coins_list:
            coin.update(self)
        self.validate_all_hearts()
        self.validate_all_coins()

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
            new_heart = Heart(self.heart_image, randint(210, 660), randint(964, 1300))
            self.heart_list.append(new_heart)
            self.like_left_to_show -= 1

    def get_new_coins(self):
        while len(self.coins_list) < 10 and self.coins_left_to_show:
            new_coin = Coins(self.coins_image, randint(1228, 1666), randint(964, 1500))
            self.coins_list.append(new_coin)
            self.coins_left_to_show -= 1

    def get_next_spin(self):
        if self.next_spin is None:
            if self.gift_engine.spin:
                self.next_spin = self.gift_engine
            elif self.like_engine.spin:
                self.next_spin = self.like_engine

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
        self.screen.blit(self.result_board, (712, 137))
        x = 728
        for type_value, value in reversed(self.last_result_list):
            if type_value == 'coins':
                self.screen.blit(self.gift_image, (x, y - (61 * next_position)))
            else:
                self.screen.blit(self.like_image, (x, y - (61 * next_position)))

            cost_surface = self.font_info.render(value, True, YELLOW)

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

    def verify_result(self, result):
        for minutes in range(10):
            if f'+ {minutes} Min' in result:
                self.plus_chron(timedelta(seconds=minutes*60) + self.bonus_time_transparent)
                self.bonus_time_transparent = timedelta(0)
            if f'+ 30 Segundos Extras na Próxima' in result:
                self.bonus_time_transparent += timedelta(seconds=30)

    def draw_qr_code(self):
        self.screen.blit(self.qrcode, (22, 462))


if __name__ == '__main__':
    game = TatiskyGame()
    game.start()

