import pygame
from random import *
import threading
import math
from pygame import image
from image_utils import *
from engine import *
from pygame import mixer
from load_files import LoadFiles
# Configurações iniciais
WIDTH, HEIGHT = 1980, 1024
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ROXO = (40, 0, 80, 120)
ROSA = (80, 0, 90, 120)
RED = (255,0,0)
SMOOTH_VALUE = 0.2
SECTORS = 12
X_POSITION = 0
Y_POSITION = 1


class ResultCountdown:
    def __init__(self, game_result_countdown, result_graphic, result_position):
        self.game_result_countdown = game_result_countdown
        self.game_result_time = datetime.now()
        self.result_graphic = result_graphic
        self.result_position = result_position


class TatiskyGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Roleta")
        self.clock = pygame.time.Clock()
        self.font_info = pygame.font.SysFont('Montserrat Heavy', 25, False)
        self.font_game_time = pygame.font.SysFont('Montserrat Heavy', 35, False)
        self.font_title = pygame.font.SysFont('Montserrat Heavy', 55, False)
        self.font_club_name = pygame.font.SysFont('Montserrat Heavy', 55, False)
        self.font_phase = pygame.font.SysFont('Montserrat Heavy', 80, False)
        self.font_counter = pygame.font.SysFont('Montserrat Heavy', 100, False)
        self.championship_extractor = ChampionshipExtractor()
        self.graphics = LoadFiles(self.championship_extractor.get_value())
        self.championship = Championship(self.graphics.club_list)
        self.actual_game = self.championship.get_next_game()
        self.last_game = None
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
        self.var_engine = Var()
        self.share_engine = Share()
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
        self.start_key_1 = False
        self.start_key_2 = False
        self.start_key_3 = False
        self.pause_game = True

        mixer.init()
        self.wheel_sound = pygame.mixer.Sound('assets/click.mp3')
        self.end_time_song = pygame.mixer.Sound('assets/ding.mp3')
        self.sub_song = pygame.mixer.Sound('assets/sub.mp3')

        self.crowd_sound = pygame.mixer.Sound('assets/torcida.mp3')
        self.goal_sound = pygame.mixer.Sound('assets/gol.mp3')
        self.var_sound = pygame.mixer.Sound('assets/var.mp3')
        self.defense_sound = pygame.mixer.Sound('assets/defesa.mp3')
        self.null_goal_sound = pygame.mixer.Sound('assets/vaia.mp3')

        self.actual_sector = 0
        self.start_game = False
        self.subscriber_name_to_draw = None
        self.all_new_subscribers = []
        self.heart_list = []
        self.like_left_to_show = 0
        self.coins_list = []
        self.coins_left_to_show = 0
        self.sharing_list = []
        self.sharing_left_to_show = 0
        self.like_rank = Ranking('liker')
        self.gift_rank = Ranking('gifter')
        self.game_result = None
        self.ball_side = 'idle'
        self.ball_position = {'right': (755, 537),
                              'left': (1176, 537),
                              'idle': (962, 943)}

        self.spinning_var = False
        # self.champion_countdown -=
        # self.champion_countdown_timer = datetime.now()

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
        y = 310
        next_position = 0
        for value in self.actual_table_values:

            if self.result is not None and next_position == self.result:
                cost_surface = value.selected_result
            else:
                cost_surface = value.result

            if value.effect.club:
                position_cost_text = (1725, y + (61 * next_position) - 18)
            else:
                position_cost_text = (1725, y + (61 * next_position))

            self.screen.blit(cost_surface, position_cost_text)
            next_position += 1

    def draw_podium(self):
        y_adjust = 298
        self.gradient_rect_podium(self.graphics.podium_image, (1377, 920))
        name_position_list = [(446+1057, 841), (368+1057, 865), (524+1057, 876)]
        points_position_list = [(420+1057, 800), (320+1057, 800), (500+1057, 800)]
        image_position_list = [(418+1057, 870), (335+1057, 890), (501+1057, 902)]
        self.screen.blit(self.graphics.podium_image, (1377, 920))
        zip_to_blit = zip(self.like_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, (name_position[0] - rank_user.name.get_width()/2,name_position[1]))
            self.screen.blit(rank_user.points, point_position)
            self.screen.blit(rank_user.image, image_position)
        self.screen.blit(self.graphics.sup_line_top_liker, (1377, 730))

        self.gradient_rect_podium(self.graphics.podium_image, (1377, 920 - y_adjust))
        name_position_list = [(446+1057, 841 - y_adjust), (368+1057, 865 - y_adjust), (524+1057, 876 - y_adjust)]
        points_position_list = [(420+1057, 800 - y_adjust), (320+1057, 800 - y_adjust), (500+1057, 800 - y_adjust)]
        image_position_list = [(418+1057, 870 - y_adjust), (335+1057, 890 - y_adjust), (501+1057, 902 - y_adjust)]
        self.screen.blit(self.graphics.podium_image, (1377, 920 - y_adjust))
        zip_to_blit = zip(self.gift_rank.rank_list, name_position_list, points_position_list, image_position_list)
        for rank_user, name_position, point_position, image_position in zip_to_blit:
            self.screen.blit(rank_user.name, (name_position[0] - rank_user.name.get_width() / 2, name_position[1]))
            self.screen.blit(rank_user.points, point_position)
            self.screen.blit(rank_user.image, image_position)
        self.screen.blit(self.graphics.sup_line_top_gifter, (1377, 730 - y_adjust))

    def gradient_rect_podium(self, target_rect, position):
        colour_rect = pygame.Surface((2, 2)).convert_alpha()
        pygame.draw.line(colour_rect, ROXO, (0, 0), (0, 1))  # left colour line
        pygame.draw.line(colour_rect, ROSA, (1, 0), (1, 1))  # right colour line
        colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.get_width(), target_rect.get_height()+160))
        self.screen.blit(colour_rect, (position[0], position[1]-160))

    def draw_roulette(self):
        rotated_wheel = pygame.transform.rotate(self.next_spin.image_wheel, self.current_angle)
        wheel_rect = rotated_wheel.get_rect(center=(357, 545))
        self.screen.blit(rotated_wheel, (wheel_rect[0], wheel_rect[1] + 150))
        self.screen.blit(self.graphics.border_wheel, (120, 476))
        if self.subscriber_name_to_draw:
            self.draw_subscriber_name()

    def draw_subscriber_name(self):
        font = pygame.font.SysFont('Montserrat Heavy', 75, False)
        cost_surface = font.render(f'Roleta do {self.subscriber_name_to_draw}', True, WHITE)
        info_board_surface = pygame.Surface((708, 100), pygame.SRCALPHA).convert_alpha()
        info_board_surface.fill((255,0,0,100))

        position_sub_name = (info_board_surface.get_width()/2 - cost_surface.get_width()/2 - 16, 372-134)
        position_info_board = (16, 353 - 134)
        position_sup_line = (81, 323 - 134)
        position_bottom_line = (81, 432 - 134)

        self.gradient_rect(info_board_surface, position_info_board)
        self.screen.blit(self.graphics.sup_line, position_sup_line)
        self.screen.blit(self.graphics.bottom_line, position_bottom_line)
        self.screen.blit(cost_surface, position_sub_name)

    def gradient_rect(self, target_rect, position):
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
                            file.write('0;0;0')
                            self.start_game = True
                    if event.key == pygame.K_c:
                        self.start_game = True

        self.var_engine.update()
        self.gift_engine.update(self)
        self.like_engine.update(self)
        self.share_engine.update(self)
        self.gift_engine.start_spin()
        self.like_engine.start_spin()
        self.share_engine.start_spin()
        while not self.running:
            if not self.like_engine.validate_extract():
                start_tki = self.font_info.render('Inicie o TKI', True, RED)
                self.screen.blit(start_tki, self.roleta_center)
                pygame.display.flip()
            else:
                self.running = True

        self.crowd_sound.set_volume(0.4)
        self.crowd_sound.play(loops=-1)
        while self.running:
            self.screen.blit(self.graphics.background, (0, 0))
            self.screen.blit(self.graphics.table, (1628, 267))
            if not self.pause_game:
                if self.actual_game:
                    self.like_engine.update(self)
                    self.gift_engine.update(self)
                    self.share_engine.update(self)
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
            if self.spinning:
                # threading.Thread(target=self.draw_spin, daemon=True).start()
                self.draw_spin()

            self.get_next_spin()
            self.draw_podium()
            self.update()

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
                    if event.key == pygame.K_p:
                        self.start_key_3 = True

                    if self.start_key_1 and self.start_key_2:
                        self.is_start_cron = not self.is_start_cron

                    if self.start_key_1 and self.start_key_3:
                        self.pause_game = not self.pause_game

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.start_key_1 = False
                    if event.key == pygame.K_t:
                        self.start_key_2 = False
                    if event.key == pygame.K_p:
                        self.start_key_3 = False

            if datetime.now() - self.result_countdown >= timedelta(milliseconds=5000):
                if self.next_spin:
                    if self.next_spin.is_spin and not self.spinning:
                        self.next_spin = None
                    elif self.next_spin.spin and not self.spinning:
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
            self.clock.tick(30)
        pygame.quit()

    def update(self):
        self.like_rank.update()
        self.gift_rank.update()

        # if len(self.heart_list) < 20:
        #     threading.Thread(target=self.get_new_hearts, daemon=True).start()
        # if len(self.coins_list) < 10:
        #     threading.Thread(target=self.get_new_coins, daemon=True).start()
        # if len(self.sharing_list) < 15:
        #     threading.Thread(target=self.get_new_sharing, daemon=True).start()

        self.get_new_hearts()
        self.get_new_coins()
        self.get_new_sharing()
        for heart in self.heart_list:
            heart.update(self)
        for coin in self.coins_list:
            coin.update(self)
        for sharing in self.sharing_list:
            sharing.update(self)

        self.validate_all_hearts()
        self.validate_all_coins()
        self.validate_all_sharing()

        self.graphics.goalkeeper.update(self)
        self.screen.blit(self.graphics.ball, self.ball_position[self.ball_side])

        if not self.pause_game:
            if self.actual_game:
                if self.actual_game.is_finish:
                    self.actual_game.update_end_game(self)
                    if self.actual_game.end_game_countdown <= 0:
                        self.championship.append_club_victory(self.actual_game.get_winner(), self.actual_game.game_next_stage)
                        self.actual_game = self.championship.get_next_game()

            if self.actual_game:
                self.actual_game.update(self)
                if self.actual_game.round_result:
                    self.update_game_result()
            else:
                self.show_champion()
            if self.game_result:
                self.show_result_countdown()

    def update_game_result(self):
        self.update_ball_goal()
        if self.next_spin.__class__.__name__ == 'Var' and self.spinning:
            pass
        else:
            if not self.actual_game.round_result.goal:
                self.defense_result()
                # self.actual_game.round_result = None
                # self.graphics.goalkeeper.get_idle()
            else:
                if self.actual_game.round_result.var:
                    self.var_result()
                    self.spinning_var = True
                else:
                    if self.actual_game.round_result:
                        if self.actual_game.round_result.goal and not self.actual_game.round_result.var and not self.spinning_var:
                            self.goal_result()

    def update_ball_goal(self):
        if not self.actual_game.round_result.get_update:
            self.actual_game.round_result.get_update = True
            self.ball_side = choice(['right', 'left'])
        if self.ball_side == 'right' and self.actual_game.round_result.goal:
            self.graphics.goalkeeper.get_right_def()
        elif self.ball_side == 'right' and not self.actual_game.round_result.goal:
            self.graphics.goalkeeper.get_left_def()
        elif self.ball_side == 'left' and self.actual_game.round_result.goal:
            self.graphics.goalkeeper.get_left_def()
        elif self.ball_side == 'left' and not self.actual_game.round_result.goal:
            self.graphics.goalkeeper.get_right_def()

    def defense_result(self):
        if not self.actual_game.round_result.get_defense:
            self.actual_game.round_result.get_defense = True
            if self.actual_game.round_result.null_goal:
                self.null_goal_sound.play()
                self.game_result = ResultCountdown(5, self.graphics.null_goal, (801, 323))
                self.actual_game.actual_club_atk.goal_chance += 0.05
            else:
                self.defense_sound.play()
                self.game_result = ResultCountdown(5, self.graphics.defense, (801, 323))
                self.actual_game.actual_club_atk.goal_chance += 0.05

    def goal_result(self):
        if not self.actual_game.round_result.get_goal:
            self.goal_sound.play()
            self.actual_game.actual_club_atk.plus_goal()
            self.game_result = ResultCountdown(10, self.graphics.goal, (801, 323))
            self.actual_game.round_result.get_goal = True

    def var_result(self):
        if not self.spinning:
            self.var_sound.play()
            self.var_engine.spin_wheel()
            self.actual_game.round_result.var = False
        self.game_result = ResultCountdown(5, self.graphics.var_board, (829, 721))

    def show_result_countdown(self):
        if datetime.now() - self.game_result.game_result_time >= timedelta(milliseconds=1000):
            self.game_result.game_result_countdown -= 1
            self.game_result.game_result_time = datetime.now()

        if self.actual_game.round_result.get_goal:
            self.screen.blit(self.actual_game.actual_club_atk.escudo_phase,
                             (WIDTH/2 - self.actual_game.actual_club_atk.escudo_phase.get_width()/2, 230))

        position_result = self.game_result.result_position
        self.screen.blit(self.game_result.result_graphic, position_result)
        if self.game_result.game_result_countdown <= 0:
            self.game_result = None
            self.graphics.goalkeeper.get_idle()
            self.ball_side = 'idle'
            if self.actual_game.round_result.goal and self.actual_game.round_result.get_goal:
                self.actual_game.change_game_time()
                self.actual_game.round_result = None
            elif self.actual_game.round_result.get_defense:
                self.actual_game.change_game_time()
                self.actual_game.round_result = None

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

    def validate_all_sharing(self):
        remove = False
        next_index = 0
        while not remove and next_index < len(self.sharing_list):
            if not self.sharing_list[next_index].is_valid:
                self.sharing_list.pop(next_index)
                remove = True
            next_index += 1

    def get_new_hearts(self):
        while len(self.heart_list) < 20 and self.like_left_to_show:
            new_heart = Heart(self.graphics.heart_image, randint(20, 120), randint(964, 1300))
            self.heart_list.append(new_heart)
            self.like_left_to_show -= 1

    def get_new_coins(self):
        while len(self.coins_list) < 10 and self.coins_left_to_show:
            new_coin = Coins(self.graphics.coins_image, randint(576, 680), randint(964, 1500))
            self.coins_list.append(new_coin)
            self.coins_left_to_show -= 1

    def get_new_sharing(self):
        while len(self.sharing_list) < 15 and self.sharing_left_to_show:
            new_sharing = Sharing(self.graphics.sharing_image, random.choice([randint(20, 120), randint(576, 680)]),
                                  randint(964, 1300))
            self.sharing_list.append(new_sharing)
            self.sharing_left_to_show -= 1

    def get_next_spin(self):
        if self.next_spin is None:
            if self.var_engine.spin:
                self.next_spin = self.var_engine
                self.next_spin.is_spin = False
            elif self.gift_engine.spin:
                self.next_spin = self.gift_engine
                self.next_spin.is_spin = False
            elif self.like_engine.spin:
                self.next_spin = self.like_engine
                self.next_spin.is_spin = False
            elif self.share_engine.spin:
                self.next_spin = self.share_engine
                self.next_spin.is_spin = False

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
        position_countdown = (55, 372)
        position_info_board = (16, 353)
        position_sup_line = (81, 323)
        position_bottom_line = (81, 432)
        self.gradient_rect(info_board_surface, position_info_board)
        self.screen.blit(self.graphics.sup_line_spin, position_sup_line)
        self.screen.blit(self.graphics.bottom_line, position_bottom_line)
        self.screen.blit(text_countdown, position_countdown)
        # self.screen.blit(cost_surface, (WIDTH/2, HEIGHT/2))

    def draw_spin(self):
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
                self.spinning_var = False
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
                    file.write(f'{self.gift_engine.all_spinning};{self.like_engine.all_spinning};{self.share_engine.all_spinning}')
                self.result_countdown = datetime.now()
                self.verify_result(self.actual_table_values[self.result])
                self.next_spin.is_spin = True

    def draw_last_result_board(self):
        y = 203
        next_position = 0
        self.screen.blit(self.graphics.result_board, (1580, 4))
        x = 1596
        for type_value, value in reversed(self.last_result_list):
            if type_value == 'coins':
                self.screen.blit(self.graphics.gift_image, (x, y - (61 * next_position)))
            elif type_value == 'likes':
                self.screen.blit(self.graphics.like_image, (x, y - (61 * next_position)))
            elif type_value == 'shares':
                self.screen.blit(self.graphics.share_image, (x+2, y - (61 * next_position) + 3))

            cost_surface = value.result

            if value.effect.club:
                position_cost_text = (x + 55, y - (61 * next_position) - 8)
            else:
                position_cost_text = (x + 55, y - (61 * next_position) + 10)
            self.screen.blit(cost_surface, position_cost_text)
            next_position += 1

        self.screen.blit(self.graphics.sup_line_time_skin, (1377, 305))
        self.screen.blit(self.graphics.cron_board, (1425, 352))
        self.get_time_string()
        if self.is_start_cron:
            cost_surface = self.font_info.render(self.transparent_time_string, True, WHITE)
        else:
            cost_surface = self.font_info.render(self.transparent_time_string, True, RED)
        cost_surface = resize(cost_surface, 3)
        position_cost_text = (1435, 363)
        self.screen.blit(cost_surface, position_cost_text)

    def transparent_time_count(self):
        if datetime.now() - self.actual_transparent_count > timedelta(seconds=1):
            self.transparent_time -= timedelta(seconds=1)
            self.actual_transparent_count = datetime.now()

    def plus_chron(self, plus_value: timedelta):
        self.actual_transparent_count = datetime.now()
        self.transparent_time += plus_value

    def verify_result(self, result):
        # for minutes in range(10):
        result.effect.apply_effect(self)
            # if f'+ {minutes} Min' in result.effect.description:
            #     self.plus_chron(timedelta(seconds=minutes*60) + self.bonus_time_transparent)
            #     self.bonus_time_transparent = timedelta(0)
            # if f'+ 30 Segundos Extras na Próxima' in result:
            #     self.bonus_time_transparent += timedelta(seconds=30)

    def draw_qr_code(self):
        self.screen.blit(self.graphics.qrcode, (22, 462))

    def show_champion(self):
        #
        # if datetime.now() - self.champion_countdown_timer >= timedelta(milliseconds=1000):
        #     self.champion_countdown -= 1
        #     self.champion_countdown_timer = datetime.now()

        position_club_shield = (770, 200)
        position_champion = (0, 0)

        self.screen.blit(self.graphics.champion, position_champion)
        self.screen.blit(self.championship.champion.escudo, position_club_shield)


if __name__ == '__main__':
    game = TatiskyGame()
    game.start()

