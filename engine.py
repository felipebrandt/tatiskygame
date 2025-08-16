import random

from extract import *
from image_utils import resize, resize_without_proportion
from pygame import image, draw, Color, Rect, font, Surface, SRCALPHA
from pygame.sprite import Sprite
from datetime import datetime
from random import randint, shuffle
from models import Webhook
import json
from load_files import Club

WIDTH, HEIGHT = 1980, 1024


class Effect:

    def __init__(self, description, value, club=None):
        self.description = description
        self.value = value
        self.club = club

    def apply_effect(self, game):
        if 'de Gol' in self.description:
            if self.club == 'club_a':
                game.actual_game.club_a.plus_goal_chance(self.value/100)
            if self.club == 'club_b':
                game.actual_game.club_b.plus_goal_chance(self.value/100)
        if 'Skin Pro' in self.description:
            game.transparent_time += timedelta(minutes=self.value)
        if 'de VAR' in self.description:
            if self.club == 'club_a':
                game.actual_game.club_a.plus_var_chance(self.value/100)
            if self.club == 'club_b':
                game.actual_game.club_b.plus_var_chance(self.value/100)
        if 'Seg ATK' in self.description:
            if self.club == 'club_a':
                game.actual_game.club_a.plus_time_atk(timedelta(seconds=self.value))
            if self.club == 'club_b':
                game.actual_game.club_b.plus_time_atk(timedelta(seconds=self.value))
        if 'Seg DEF' in self.description:
            if self.club == 'club_a':
                game.actual_game.club_a.plus_time_def(timedelta(seconds=self.value))
            if self.club == 'club_b':
                game.actual_game.club_b.plus_time_def(timedelta(seconds=self.value))
        if 'Impedimento' in self.description:
            game.actual_game.round_result.goal = False
            game.actual_game.round_result.null_goal = True
        if 'Falta de Ataque' in self.description:
            game.actual_game.round_result.goal = False
            game.actual_game.round_result.null_goal = True
        if 'Gol de Mão' in self.description:
            game.actual_game.round_result.goal = False
            game.actual_game.round_result.null_goal = True


class TableResult:
    def __init__(self, effect, club=None):
        self.result, self.selected_result = self.get_result_surface(effect.description, club)
        self.effect = effect

    @staticmethod
    def get_result_surface(string_result, club):
        font_info = font.SysFont('Montserrat Heavy', 40, False)
        selected = font_info.render(string_result,
                              True,
                              (255, 255, 0))
        not_selected = font_info.render(string_result,
                              True,
                              (255, 255, 255))

        if club:
            width_total = club.escudo_icon.get_width() + not_selected.get_width()
            height_total = max(club.escudo_icon.get_height(), not_selected.get_height())
            combined_surface_selected = Surface((width_total, height_total), SRCALPHA)
            combined_surface_not_selected = Surface((width_total, height_total), SRCALPHA)
            combined_surface_selected.blit(club.escudo_icon, (0, 0))
            combined_surface_selected.blit(selected, (club.escudo_icon.get_width(),
                                                           (height_total - selected.get_height()) // 2))
            combined_surface_not_selected.blit(club.escudo_icon, (0, 0))
            combined_surface_not_selected.blit(not_selected,(club.escudo_icon.get_width(),
                                                              (height_total - not_selected.get_height()) // 2))
        else:
            width_total = not_selected.get_width()
            height_total = not_selected.get_height()
            combined_surface_selected = Surface((width_total, height_total), SRCALPHA)
            combined_surface_not_selected = Surface((width_total, height_total), SRCALPHA)
            combined_surface_selected.blit(selected, (0, 0))
            combined_surface_not_selected.blit(not_selected, (0, 0))
        return combined_surface_not_selected, combined_surface_selected


class Wheel:
    def __init__(self):
        self.actual_level = 1
        self.xp_points = 0
        self.xp_next_level = 0
        self.like_amount = 0
        self.like_to_show = 0
        self.spin = 0
        self.all_spinning = 0
        self.spot_level_list = []
        self.level_grid = []
        self.table = []
        self.table_type = None
        self.image_wheel = None
        self.subscriber_name_list = list()
        self.is_spin = False

    def start_spin(self):
        with open('spin.csv') as file:
            gift, likes, share = file.read().split(';')
        if self.table_type == 'coins':
            self.all_spinning = int(gift)
        elif self.table_type == 'share':
            self.all_spinning = int(share)
        else:
            self.all_spinning = int(likes)

        self.spin_wheel()
        self.spin -= self.all_spinning

    def get_level_grid(self):
        if self.table_type == 'coins':
            self.level_grid = [0, 3000, 6000, 10000, 15000, 24000, 36000, 51000, 75000, 120000]
        elif self.table_type == 'share':
            self.level_grid = [0, 3000, 6000, 10000, 15000, 24000, 36000, 51000, 75000, 120000]
        else:
            self.level_grid = [0, 100000, 200000, 350000, 500000, 700000, 1000000, 1400000, 1900000, 2500000]

    def spin_wheel(self):
        while self.like_to_show >= self.divisor:
            self.spin += 1
            self.like_to_show -= self.divisor

    # def get_new_level(self):
    #     if self.actual_level < len(self.level_grid):
    #         if self.xp_points >= self.level_grid[self.actual_level]:
    #             self.actual_level += 1
    #             self.table_results()

    def table_results(self, club_a: Club, club_b: Club):
        club_results, tatisky_results = self.get_table_type()
        next_club = 0
        self.table = []
        for club_result in club_results:
            if next_club:
                actual_club = club_b
                next_club -= 1
            else:
                actual_club = club_a
                next_club += 1
            self.table.append(TableResult(club_result, actual_club))

        for tatisky_result in tatisky_results:
            self.table.append(TableResult(tatisky_result))

    def get_table_type(self):

        if self.table_type == 'coins':
            club = [Effect('+ 5% de Gol', 5, 'club_a'), Effect('+ 5% de Gol', 5, 'club_b'),
                    Effect('+ 10% de Gol', 10, 'club_a'), Effect('+ 10% de Gol', 10, 'club_b'),
                    Effect('+ 15% de Gol', 15, 'club_a'), Effect('+ 15% de Gol', 15, 'club_b'),
                    ]
            tatisky = [Effect('+1 Min Skin Pro', 1), Effect('+1 Min Skin Pro', 1),
                       Effect('+2 Min Skin Pro', 2), Effect('+2 Min Skin Pro', 2),
                       Effect('+3 Min Skin Pro', 3), Effect('+4 Min Skin Pro', 4)]
        elif self.table_type == 'shares':
            club = [Effect('+ 15% de VAR', 15, 'club_a'), Effect('+ 15% de VAR', 15, 'club_b'),
                    Effect('+ 20% de VAR', 20, 'club_a'), Effect('+ 20% de VAR', 20, 'club_b'),
                    Effect('+ 25% de VAR', 25, 'club_a'), Effect('+ 25% de VAR', 25, 'club_b'),
                    ]
            tatisky = [Effect('Carinho', 0), Effect('Troca a Skin', 0), Effect('Fica de Pé', 0),
                       Effect( 'Dança Gatinha', 0), Effect('Mostra o Look', 0), Effect('Dança na Cadeira', 0)]
        else:
            club = [Effect('+ 5 Seg ATK', 5, 'club_a'), Effect('+ 5 Seg ATK', 5, 'club_b'),
                    Effect('+ 5 Seg DEF', 5, 'club_a'), Effect('+ 5 Seg DEF', 5, 'club_b'),
                    Effect('+ 10 Seg ATK', 10, 'club_a'), Effect('+ 10 Seg ATK', 10, 'club_b'),
                    Effect('+ 10 Seg DEF', 10, 'club_a'), Effect('+ 10 Seg DEF', 10, 'club_b')
                    ]
            tatisky = [Effect('Manda um Beijo', 0), Effect('Faz um Brinde', 0),
                       Effect('Desfila', 0), Effect('Faz Pose', 0)]

        return club, tatisky

    def start_wheel(self, type_wheel):
        self.table_type = type_wheel
        self.image_wheel = image.load(f'assets/wheel_{type_wheel}.png').convert_alpha()
        self.get_level_grid()


class Bar:
    def __init__(self):
        self.bar_foreground = None
        self.bar_background = None
        self.icon = None
        self.extract = None
        self.location = None
        self.divisor = None
        self.level_icon = None

    def start_bar(self, type_extractor, divisor, icon_location, bar_location, size):
        self.bar_foreground = resize_without_proportion(image.load('assets/bar_foreground.png').convert_alpha(),
                                                        0.5, 0.75)
        self.bar_background = resize_without_proportion(image.load('assets/bar_background.png').convert_alpha(),
                                                        0.5, 0.75)
        self.icon = resize(image.load(f'assets/{type_extractor}.png').convert_alpha(), size)
        self.extract = Extractor(type_extractor)
        self.location = {'icon': icon_location,
                         'bar': bar_location}
        self.divisor = divisor
        self.level_icon = resize(image.load(f'assets/level.png').convert_alpha(), 0.25)

    def get_last_amount_string(self):
        return f'{(self.like_to_show % self.divisor)}/{self.divisor}'

    def draw_bar(self, game):
        font_title = font.SysFont('Montserrat Heavy', 60, False)
        game.screen.blit(self.icon, self.location['icon'])
        game.screen.blit(self.bar_background, self.location['bar'])
        draw.rect(game.screen,
                  Color(255, 0, 0),
                  Rect(self.location['bar'][0] + 8, self.location['bar'][1] + 8,
                       455 * (self.like_to_show / self.divisor), 24))

        cost_surface = font_title.render(self.get_last_amount_string(), True, (255, 255, 255))
        position_cost_text = (
        self.bar_foreground.get_width() / 2 - cost_surface.get_width() / 2 + self.location['bar'][0],
        self.bar_foreground.get_height() / 2 - cost_surface.get_height() / 2 + self.location['bar'][1])

        game.screen.blit(self.bar_foreground, self.location['bar'])
        game.screen.blit(cost_surface, position_cost_text)


class Like(Wheel, Bar):
    def __init__(self):
        super().__init__()
        self.start_bar('likes', 5000, (0, 65), (70, 79), 0.15)
        self.start_wheel('likes')
        self.next_extract = datetime.now()
        self.is_possible_extract = True

    def update_extract_status(self, status):
        self.is_possible_extract = status
        self.next_extract = datetime.now() + timedelta(seconds=10)

    def update(self, game):
        self.table_results(game.actual_game.club_a, game.actual_game.club_b)
        if self.next_extract <= datetime.now():
            if self.is_possible_extract:
                actual_like_count = self.extract.get_value()
                plus_like = actual_like_count - self.like_amount
                game.like_left_to_show += plus_like
                self.like_to_show += plus_like
                self.like_amount = actual_like_count
                self.xp_points = self.like_amount * 10
                self.spin_wheel()
            self.next_extract += timedelta(seconds=10)
        self.draw_bar(game)

    def force_extract(self, game):
        actual_like_count = self.extract.get_value()
        plus_like = actual_like_count - self.like_amount
        game.like_left_to_show += plus_like
        self.like_to_show += plus_like
        self.like_amount = actual_like_count
        self.xp_points = self.like_amount * 10
        self.spin_wheel()
        return plus_like

    def validate_extract(self):
        response = False
        if self.next_extract <= datetime.now():
            response = self.extract.is_possible_extract()
            self.next_extract += timedelta(seconds=10)
        return response


class Gift(Wheel, Bar):
    def __init__(self):
        super().__init__()
        self.start_bar('coins', 100, (0, 5), (70, 18), 0.1)
        self.start_wheel('coins')
        self.next_extract = datetime.now()
        self.sub_name_extractor = Extractor('name')

    def update(self, game):
        self.table_results(game.actual_game.club_a, game.actual_game.club_b)
        if self.next_extract <= datetime.now():
            actual_like_count = self.extract.get_value()
            game.coins_left_to_show += actual_like_count - self.like_amount
            self.like_to_show += actual_like_count - self.like_amount
            self.like_amount = actual_like_count
            self.xp_points = self.like_amount * 10
            self.get_sub_name_livepix(game)
            self.get_sub_name_tiktok(game)
            self.spin_wheel()
            self.next_extract += timedelta(seconds=10)
        # self.get_new_level()
        self.draw_bar(game)

    # def get_sub_spin(self):
    #     cloud_subs = self.sub_extractor.get_value()
    #     while cloud_subs > self.sub_amount:
    #         self.spin += 1
    #         self.sub_spinning += 1
    #         self.sub_amount += 1
    #     self.get_sub_name()

    def get_sub_name_tiktok(self, game):
        new_subscriber = self.sub_name_extractor.get_sub_name()
        if new_subscriber and new_subscriber not in game.all_new_subscribers:
            game.all_new_subscribers.append(new_subscriber)
            self.spin += 1
            self.subscriber_name_list.append(new_subscriber)

    def get_sub_name_livepix(self, game):
        webhook_list = Webhook.select().where(Webhook.updated_at.is_null())
        for new_webhook in webhook_list:
            webhook_json = json.loads(new_webhook.raw_data)
            try:
                if webhook_json['resource']['type'] == "subscription" and webhook_json['event'] == "new":
                    new_subscriber = "Discord / Livepix"
                    game.all_new_subscribers.append(new_subscriber)
                    self.spin += 1
                    self.subscriber_name_list.append(new_subscriber)
                new_webhook.updated_at = datetime.now()
                new_webhook.save()
            except Exception as e:
                new_webhook.updated_at = datetime.now()
                new_webhook.save()

    def validate_extract(self):
        response = False
        if self.next_extract <= datetime.now():
            response = self.extract.is_possible_extract()
            self.next_extract += timedelta(seconds=10)
        return response


class Share(Wheel, Bar):
    def __init__(self):
        super().__init__()
        self.start_bar('shares', 50, (5, 130), (70, 140), 0.05)
        self.start_wheel('shares')
        self.next_extract = datetime.now()

    def update(self, game):
        self.table_results(game.actual_game.club_a, game.actual_game.club_b)
        if self.next_extract <= datetime.now():
            actual_like_count = self.extract.get_value()
            game.sharing_left_to_show += actual_like_count - self.like_amount
            self.like_to_show += actual_like_count - self.like_amount
            self.like_amount = actual_like_count
            self.xp_points = self.like_amount * 10
            self.spin_wheel()
            self.next_extract += timedelta(seconds=10)
        # self.get_new_level()
        self.draw_bar(game)

    def validate_extract(self):
        response = False
        if self.next_extract <= datetime.now():
            response = self.extract.is_possible_extract()
            self.next_extract += timedelta(seconds=10)
        return response


class Var(Wheel):
    def __init__(self):
        super().__init__()
        self.start_wheel('var')

    def update(self):
        self.var_table_results()

    def spin_wheel(self):
        self.spin += 1

    def var_table_results(self):
        table_results = [Effect('Goooool', 0), Effect('Goooool', 0), Effect('Goooool', 0), Effect('Goooool', 0),
                         Effect('Goooool', 0), Effect('Goooool', 0), Effect('Goooool', 0), Effect('Goooool', 0),
                         Effect('Goooool', 0), Effect('Impedimento', 1), Effect('Falta de Ataque', 1),
                         Effect('Gol de Mão', 1)]
        for table_result in table_results:
            self.table.append(TableResult(table_result))


class Subscription(Wheel, Bar):
    pass


class Pix(Bar):
    pass


class Heart:

    def __init__(self, heart_image, position_x, position_y):
        self.image = heart_image
        self.position_y = position_y
        self.position_x = position_x
        self.is_valid = True

    def update(self, game):
        game.screen.blit(self.image, (self.position_x, self.position_y))
        self.actualize_position()
        self.validate_heart()

    def actualize_position(self):
        plus_x = randint(-2, 2)
        plus_y = randint(3, 6)
        self.position_y -= plus_y
        self.position_x += plus_x

    def validate_heart(self):
        if self.position_y <= 265:
            self.is_valid = False


class Coins:

    def __init__(self, coin_image, position_x, position_y):
        self.image = coin_image
        self.position_y = position_y
        self.position_x = position_x
        self.is_valid = True

    def update(self, game):
        game.screen.blit(self.image, (self.position_x, self.position_y))
        self.actualize_position()
        self.validate_coin()

    def actualize_position(self):
        plus_x = randint(-2, 2)
        plus_y = randint(3, 6)
        self.position_y -= plus_y
        self.position_x += plus_x

    def validate_coin(self):
        if self.position_y <= 265:
            self.is_valid = False


class Sharing:

    def __init__(self, share_image, position_x, position_y):
        self.image = share_image
        self.position_y = position_y
        self.position_x = position_x
        self.is_valid = True

    def update(self, game):
        game.screen.blit(self.image, (self.position_x, self.position_y))
        self.actualize_position()
        self.validate_sharing()

    def actualize_position(self):
        plus_x = randint(-2, 2)
        plus_y = randint(3, 6)
        self.position_y -= plus_y
        self.position_x += plus_x

    def validate_sharing(self):
        if self.position_y <= 265:
            self.is_valid = False


class RoundResult:
    def __init__(self, goal, var):
        self.goal = goal
        self.var = var
        self.get_goal = False
        self.get_defense = False
        self.get_update = False
        self.null_goal = False


# class TimeCountdown:
#     def __init__(self, countdown_seconds, delay, string_show_message, color_message, font_message, has_info_board):
#         self.countdown_seconds = countdown_seconds
#         self.delay = delay
#         self.string_show_message = string_show_message
#         self.color_message = color_message
#         self.font_message = font_message
#         self.start_countdown = datetime.now()
#         self.has_info_board = has_info_board
#
#     def update_countdown(self, game):
#         if datetime.now() - self.start_countdown <= timedelta(milliseconds=self.delay):
#             text_countdown = self.font_message.render(self.string_show_message.format(countdown=self.countdown_seconds),
#                                                       True, self.color_message)
#         else:
#             self.countdown_seconds -= 1
#             self.start_countdown = datetime.now()
#             text_countdown = self.font_message.render(self.string_show_message.format(countdown=self.countdown_seconds),
#                                                       True, self.color_message)
#
#         phase = 'o Ataque'
#         actual_club = self.actual_club_atk
#         if self.phase_game:
#             phase = 'a Defesa'
#             actual_club = self.actual_club_def
#
#         club_text = game.font_title.render(f'{actual_club.club_name} iniciará {phase} em:', True, (255, 255, 255))
#         info_board_surface = Surface((text_countdown.get_width() + 100, 120), SRCALPHA).convert_alpha()
#         info_board_surface.fill((255, 0, 0, 100))
#         position_countdown = (WIDTH/2 - text_countdown.get_width()/2, 405)
#         position_info_board = (WIDTH/2 - info_board_surface.get_width()/2, 353)
#         position_club_text = (WIDTH/2 - club_text.get_width()/2, 358)
#         game.gradient_rect(info_board_surface, position_info_board)
#         game.screen.blit(club_text, position_club_text)
#         game.screen.blit(text_countdown, position_countdown)

class Game:

    def __init__(self, game_tuple, game_stage, game_next_stage):
        self.club_a = game_tuple[0]
        self.club_b = game_tuple[1]
        self.stage = game_stage
        self.game_next_stage = game_next_stage
        self.actual_club_atk: Club = None
        self.actual_club_def: Club = None
        self.is_start_round = False
        self.phase_game = 0 # 0 = atk 1 = def
        self.phase_countdown = 0
        self.is_compute = False
        self.round_result = None
        self.is_starting = datetime.now()
        self.phase_time = datetime.now()
        self.start_countdown = 3
        self.period = 1
        self.game_time = timedelta(seconds=0)
        self.period_countdown = 0
        self.period_time = datetime.now()
        self.is_finish = False
        self.period_time_max = 2700
        self.is_penalty = False
        self.is_start = True
        self.start_game_time = datetime.now()
        self.start_game_countdown = 5
        self.end_game_time = datetime.now()
        self.end_game_countdown = 5

    def get_winner(self):
        if self.club_a.goal > self.club_b.goal:
            return self.club_a
        return self.club_b

    def is_tie_status(self):
        return self.club_a.goal == self.club_b.goal

    def start_round(self):
        if self.actual_club_atk:
            self.change_clubs()
        else:
            self.actual_club_atk = self.club_a
            self.actual_club_def = self.club_b
        self.actual_club_atk.end_act = datetime.now() + self.actual_club_atk.time_atk
        self.is_start_round = True
        self.phase_game = 0
        self.actual_club_atk.crowd_scream = 0
        self.actual_club_def.crowd_scream = 0
        self.start_countdown = 3
        self.is_starting = datetime.now()
        self.start_atk_phase()

    def start_game(self, game):
        if datetime.now() - self.start_game_time >= timedelta(milliseconds=1000):
            self.start_game_countdown -= 1
            self.start_game_time = datetime.now()

        if self.start_game_countdown <= 0:
            self.is_start = False

        phase_text = game.font_phase.render(self.stage.capitalize(), True, (255, 255, 255))
        vs_text = game.font_title.render('VS', True, (255, 255, 255))
        stage_text = game.font_phase.render('Primeiro Tempo', True, (255, 255, 255))

        clubs_board = Surface((300, 100), SRCALPHA).convert_alpha()
        clubs_board.blit(self.club_a.escudo_phase, (0, 0))
        clubs_board.blit(vs_text, (100 + (100/2) - vs_text.get_width()/2,
                                   clubs_board.get_height()/2 - vs_text.get_height()/2))
        clubs_board.blit(self.club_b.escudo_phase, (200, 0))

        info_board_surface = Surface((stage_text.get_width() + 20, 300), SRCALPHA).convert_alpha()
        info_board_surface.fill((0, 0, 0, 100))

        position_phase_text = (WIDTH / 2 - phase_text.get_width() / 2, 360)
        position_clubs_board = (WIDTH / 2 - clubs_board.get_width() / 2, 455)
        position_stage_text = (WIDTH / 2 - stage_text.get_width() / 2, 580)

        position_info_board = (WIDTH / 2 - info_board_surface.get_width() / 2, 353)

        game.gradient_rect(info_board_surface, position_info_board)

        game.screen.blit(phase_text, position_phase_text)
        game.screen.blit(clubs_board, position_clubs_board)
        game.screen.blit(stage_text, position_stage_text)

    def start_atk_phase(self):
        self.phase_countdown = self.actual_club_atk.time_atk.seconds
        self.phase_time = datetime.now()

    def start_def_phase(self):
        self.phase_game = 1
        self.start_countdown = 3
        self.is_starting = datetime.now()
        self.actual_club_def.end_act = datetime.now() + self.actual_club_def.time_def
        self.phase_countdown = self.actual_club_def.time_def.seconds
        self.phase_time = datetime.now()

    def is_phase_atk(self):
        return True if self.phase_game == 0 else False

    def update(self, game):
        if not self.is_start:
            if not self.is_finish:
                if not self.period_countdown:
                    if not self.round_result:
                        if not self.is_compute:
                            if not self.is_start_round:
                                self.start_round()
                                game.like_engine.update_extract_status(False)
                                game.like_engine.force_extract(game)
                            elif self.start_countdown <= 0:
                                if self.is_phase_atk():
                                    if self.phase_countdown > 0:
                                        self.update_phase_countdown(game)
                                    else:
                                        self.actual_club_atk.crowd_scream = game.like_engine.force_extract(game)
                                        self.start_def_phase()

                                if not self.is_phase_atk():
                                    if self.phase_countdown > 0:
                                        self.update_phase_countdown(game)
                                    else:
                                        self.actual_club_def.crowd_scream = game.like_engine.force_extract(game)
                                        self.is_compute = True
                                        game.like_engine.update_extract_status(True)
                            else:
                                self.update_countdown(game)
                        elif not self.round_result:
                            if self.period_time_max < 2700:
                                self.tie_solve_temp()
                            else:
                                self.compute_round()
                else:
                    self.update_game_break(game)
                self.draw_score_board(game)
        else:
            self.start_game(game)

    def change_game_time(self):
        self.game_time += timedelta(seconds=450)
        if self.game_time.seconds == self.period_time_max:
            self.change_period()
            self.game_time = timedelta(seconds=0)
            self.game_break()
            return

    def game_break(self):
        self.period_countdown = 5
        self.period_time = datetime.now()

    def change_period(self):
        if self.period == 2:
            self.end_game()
            return
        self.period += 1
        return

    def end_game(self):
        if not self.is_tie_status():
            self.is_finish = True
            self.print_result()
        elif self.period_time_max == 2700:
            self.period_time_max = 900
            self.period = 1
        else:
            self.is_penalty = True
            self.club_a.goal = self.club_b.goal = 0

    def get_time_string(self):
        minute = self.game_time.seconds // 60
        second = self.game_time.seconds % 60
        minute_string = str(minute)
        if len(minute_string) == 1:
            minute_string = '0' + minute_string

        second_string = str(second)
        if len(second_string) == 1:
            second_string = '0' + second_string

        return f'{minute_string if minute else "00"}:{second_string if second else "00"}'

    def draw_score_board(self, game):
        game.screen.blit(game.graphics.scoreboard, (WIDTH/2-game.graphics.scoreboard.get_width()/2, 77))
        period = game.font_title.render(f'{self.period}{"T" if self.period_time_max >= 2700 else "P" }',
                                        True, (255, 255, 255))
        game_time = game.font_title.render(f'{self.get_time_string()}', True, (0, 0, 0))
        game.screen.blit(period, (906, 78))
        game.screen.blit(game_time, (972, 78))

        game.screen.blit(self.club_a.escudo_scoreboard, (584, 108))
        club_a_name = game.font_club_name.render(f'{self.adjust_name(self.club_a.club_name)}', True, (0, 0, 0))
        game.screen.blit(club_a_name, (850 - 196/2 - club_a_name.get_width()/2, 125))

        game.screen.blit(self.club_b.escudo_scoreboard, (1330, 108))
        club_b_name = game.font_club_name.render(f'{self.adjust_name(self.club_b.club_name)}', True, (0, 0, 0))
        game.screen.blit(club_b_name, (1110 + 196/2 - club_b_name.get_width()/2, 125))

        score = game.font_counter.render(f'{self.club_a.goal}-{self.club_b.goal}', True, (255, 255, 255))

        game.screen.blit(score, (940, 110))

        if self.is_penalty:
            pass

    def adjust_name(self, club_name):
        if len(club_name) >= 13:
            return club_name[:5]
        return club_name

    def compute_round(self):
        crowd_goal_chance = self.get_crowd_goal_chance_value()
        shot_goal = random.random()
        var_goal = random.random()
        goal = False
        var = False
        penalty_mod = 0
        if self.is_penalty:
            penalty_mod = 0.1
        if shot_goal <= crowd_goal_chance + self.actual_club_atk.get_goal_chance() + penalty_mod:
            goal = True
            if var_goal <= self.get_var_chance(crowd_goal_chance + self.actual_club_atk.get_goal_chance()) and \
                    not self.is_penalty:
                var = True

        self.round_result = RoundResult(goal, var)
        self.end_round()

    def tie_solve_temp(self):
        if self.period == 2 and self.game_time.seconds == 450 and self.is_tie_status():
            self.round_result = RoundResult(True, False)
            self.end_round()
        elif self.period == 2 and self.game_time.seconds == 450 and not self.is_tie_status():
            self.round_result = RoundResult(False, False)
            self.end_round()
        else:
            self.compute_round()

    def end_round(self):
        self.is_compute = False
        self.is_start_round = False

    def get_var_chance(self, goal_chance):
        if goal_chance >= 0.4:
            return self.actual_club_def.var_chance + 0.2
        return self.actual_club_def.var_chance

    def get_crowd_goal_chance_value(self):
        crowd_mod = 0
        if self.actual_club_atk.crowd_scream > 150:
            crowd_mod = 0.04
        if self.actual_club_atk.crowd_scream > 650:
            crowd_mod = 0.08
        if self.actual_club_atk.crowd_scream > 1000:
            crowd_mod = 0.12
        if self.actual_club_atk.crowd_scream:
            crowd_atk = self.actual_club_atk.crowd_scream / (self.actual_club_atk.crowd_scream + self.actual_club_def.crowd_scream)
            if crowd_atk < 0.2:
                return 0.07 + crowd_mod
            if 0.2 <= crowd_atk < 0.5:
                return 0.10 + crowd_mod
            if 0.5 <= crowd_atk <= 0.7:
                return 0.13 + crowd_mod
            if crowd_atk > 0.7:
                return 0.18 + crowd_mod
        return 0.0

    def change_clubs(self):
        to_change = self.actual_club_atk
        self.actual_club_atk = self.actual_club_def
        self.actual_club_def = to_change

    def update_countdown(self, game):
        if datetime.now() - self.is_starting <= timedelta(milliseconds=1500):
            text_countdown = game.font_counter.render('               ' + str(self.start_countdown) + '               ',
                                                      True, (255, 255, 255))
        else:
            self.start_countdown -= 1
            self.is_starting = datetime.now()
            text_countdown = game.font_counter.render('               ' + str(self.start_countdown) + '               ',
                                                      True, (255, 255, 255))

        phase = 'o Ataque'
        actual_club = self.actual_club_atk
        if self.phase_game:
            phase = 'a Defesa'
            actual_club = self.actual_club_def

        club_text = game.font_title.render(f'{actual_club.club_name} iniciará {phase} em:', True, (255, 255, 255))
        info_board_surface = Surface((text_countdown.get_width() + 100, 120), SRCALPHA).convert_alpha()
        info_board_surface.fill((255, 0, 0, 100))
        position_countdown = (WIDTH/2 - text_countdown.get_width()/2, 232)
        position_info_board = (WIDTH/2 - info_board_surface.get_width()/2, 180)
        position_club_text = (WIDTH/2 - club_text.get_width()/2, 185)
        game.gradient_rect(info_board_surface, position_info_board)
        game.screen.blit(club_text, position_club_text)
        game.screen.blit(text_countdown, position_countdown)

    def update_phase_countdown(self, game):
        if datetime.now() - self.phase_time <= timedelta(milliseconds=1000):
            text_countdown = game.font_counter.render(str(self.phase_countdown), True, (255, 0, 0))
        else:
            self.phase_countdown -= 1
            self.phase_time = datetime.now()
            text_countdown = game.font_counter.render(str(self.phase_countdown), True, (255, 0, 0))

        phase = 'Ataque do'
        actual_club = self.actual_club_atk
        if self.phase_game:
            phase = 'Defesa do'
            actual_club = self.actual_club_def

        club_text = game.font_counter.render(f'{phase} {actual_club.club_name}', True, (255, 255, 0))
        position_countdown = (WIDTH/2 - text_countdown.get_width()/2, 267)
        position_club_text = (WIDTH/2 - club_text.get_width()/2, 180)
        game.screen.blit(club_text, position_club_text)
        game.screen.blit(text_countdown, position_countdown)

    def update_end_game(self, game):
        if datetime.now() - self.end_game_time >= timedelta(milliseconds=1000):
            self.end_game_countdown -= 1
            self.end_game_time = datetime.now()

        string_stage = "Final de Jogo"
        stage_text = game.font_phase.render(string_stage, True, (255, 255, 255))
        vs_text = game.font_counter.render(f'{self.club_a.goal}-{self.club_b.goal}', True, (255, 255, 255))

        clubs_board = Surface((400, 100), SRCALPHA).convert_alpha()
        clubs_board.blit(self.club_a.escudo_phase, (0, 0))
        clubs_board.blit(vs_text, (100 + (200 / 2) - vs_text.get_width() / 2,
                                   clubs_board.get_height() / 2 - vs_text.get_height() / 2))
        clubs_board.blit(self.club_b.escudo_phase, (300, 0))

        info_board_surface = Surface((stage_text.get_width() + 100, 200), SRCALPHA).convert_alpha()
        info_board_surface.fill((255, 0, 0, 100))

        position_stage_text = (WIDTH / 2 - stage_text.get_width() / 2, 360)
        position_clubs_board = (WIDTH / 2 - clubs_board.get_width() / 2, 455)

        position_info_board = (WIDTH / 2 - info_board_surface.get_width() / 2, 353)

        game.gradient_rect(info_board_surface, position_info_board)

        game.screen.blit(clubs_board, position_clubs_board)
        game.screen.blit(stage_text, position_stage_text)

    def update_game_break(self, game):
        if datetime.now() - self.period_time >= timedelta(milliseconds=1000):
            self.period_countdown -= 1
            self.period_time = datetime.now()

        string_stage = self.get_string_stage()
        stage_text = game.font_phase.render(string_stage, True, (255, 255, 255))
        vs_text = game.font_counter.render(f'{self.club_a.goal}-{self.club_b.goal}', True, (255, 255, 255))

        clubs_board = Surface((400, 100), SRCALPHA).convert_alpha()
        clubs_board.blit(self.club_a.escudo_phase, (0, 0))
        clubs_board.blit(vs_text, (100 + (200 / 2) - vs_text.get_width() / 2,
                                   clubs_board.get_height() / 2 - vs_text.get_height() / 2))
        clubs_board.blit(self.club_b.escudo_phase, (300, 0))

        info_board_surface = Surface((stage_text.get_width() + 100, 200), SRCALPHA).convert_alpha()
        info_board_surface.fill((255, 0, 0, 100))

        position_stage_text = (WIDTH / 2 - stage_text.get_width() / 2, 360)
        position_clubs_board = (WIDTH / 2 - clubs_board.get_width() / 2, 455)

        position_info_board = (WIDTH / 2 - info_board_surface.get_width() / 2, 353)

        game.gradient_rect(info_board_surface, position_info_board)

        game.screen.blit(clubs_board, position_clubs_board)
        game.screen.blit(stage_text, position_stage_text)

    def print_result(self):
        print(f'Jogo Finalizado: {self.club_a.club_name} {self.club_a.goal} x {self.club_b.goal} {self.club_b.club_name}')

    def get_string_stage(self):
        if self.period_time_max >= 2700:
            return 'Segundo Tempo'
        else:
            if self.period == 1:
                return '1º Tempo da Prorrogação '
            return '2º Tempo da Prorrogação '


class Championship:

    def __init__(self, club_list):
        self.games = {'oitavas': [],
                      'quartas': [],
                      'semi': [],
                      'final': []}
        self.mount_games(club_list)
        self.champion: Club = None
        self.club_victory = []

    def mount_games(self, club_list):
        # shuffle(club_list)
        while club_list:
            club_a = club_list.pop()
            club_b = club_list.pop()
            self.games['oitavas'].append((club_a, club_b))

    def get_next_game(self):
        if self.games['oitavas']:
            return Game(self.games['oitavas'].pop(),'oitavas' , 'quartas')

        if self.games['quartas']:
            return Game(self.games['quartas'].pop(), 'quartas', 'semi')

        if self.games['semi']:
            return Game(self.games['semi'].pop(), 'semi', 'final')

        if self.games['final']:
            return Game(self.games['final'].pop(), 'final', None)

        return None

    def insert_new_game(self, stage, club_a, club_b):
        self.games[stage].append((club_a, club_b))

    def append_club_victory(self, club: Club, next_phase):
        if next_phase:
            club.restart()
            self.club_victory.append(club)
            if len(self.club_victory) == 2:
                self.games[next_phase].append(tuple(self.club_victory))
                self.club_victory = []
        else:
            self.champion = club


class GamesIcon:

    def __init__(self, icon_image):
        self.image = icon_image
        self.position_y = 20
        self.position_x = 1313
        self.is_valid = True

    def update(self, game):
        game.screen.blit(self.image, (self.position_x, self.position_y))
        self.actualize_position()
        self.validate_sharing()

    def actualize_position(self):
        self.position_x -= 5

    def validate_sharing(self):
        if self.position_x <= 265:
            self.is_valid = False


class PreviewGamesBoard:
    pass


if __name__ == '__main__':
    gift = Gift()
    gift.get_sub_name_livepix()


