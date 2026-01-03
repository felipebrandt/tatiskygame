from extract import *
from image_utils import *
from pygame import image, draw, Color, Rect
from datetime import datetime
from random import randint, shuffle
from models import Webhook, Dare, WordModel
import json
from imap import get_privacy_sell
from pygame_utils_ts import draw_gradient_rect


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
        self.table = None
        self.table_type = None
        self.image_wheel = None
        self.subscriber_name_list = list()
        self.lush_on = False

    def get_table_type_integer(self):
        if self.table_type == 'likes':
            return 0
        if self.table_type == 'coins':
            return 1
        if self.table_type == 'subscribe':
            return 2

    def start_spin(self):
        with open('spin.csv') as file:
            gift, likes = file.read().split(';')
        if self.table_type == 'coins':
            self.all_spinning = int(gift)
        else:
            self.all_spinning = int(likes)

        self.spin_wheel()
        self.spin -= self.all_spinning

    def get_level_grid(self):
        if self.table_type == 'coins':
            self.level_grid = [0, 3000, 6000, 10000, 15000, 24000, 36000, 51000, 75000, 120000]
        else:
            self.level_grid = [0, 100000, 200000, 350000, 500000, 700000, 1000000, 1400000, 1900000, 2500000]

    def spin_wheel(self):
        while self.like_to_show >= self.divisor:
            self.spin += 1
            self.like_to_show -= self.divisor

    def get_new_level(self):
        if self.actual_level < len(self.level_grid):
            if self.xp_points >= self.level_grid[self.actual_level]:
                self.actual_level += 1
                self.table_results([])

    @staticmethod
    def remove_last_results(results, table):
        if results:
            for result in results:
                if result in table:
                    table.remove(result)
        return table

    def get_distribution(self, table_type):
        if table_type == 0:
            low = max(0, 8 - self.actual_level)
            mid = max(1, self.actual_level // 2 + 2)
            high = 12 - (low + mid)
        elif table_type == 1:
            low = max(0, 5 - (self.actual_level - 1))
            if self.actual_level <= 2:
                mid = 4
            elif self.actual_level <= 5:
                mid = 3
            elif self.actual_level <= 7:
                mid = 2
            elif self.actual_level <= 9:
                mid = 1
            else:
                mid = 0

            high = min(3, (self.actual_level // 3))
        else:
            low = 0
            mid = 3
            high = 3

        return low, mid, high

    def table_results(self, result_list):
        integer_table_type = self.get_table_type_integer()
        all_dare = Dare.get_dare_type(integer_table_type, self.lush_on, result_list)
        low, mid, high = self.get_distribution(integer_table_type)

        self.table = all_dare['light_dare'][:low] + all_dare['medium_dare'][:mid] + all_dare['hard_dare'][:high]

        if integer_table_type != 0:
            plus_results = 12 - len(self.table)
            for time_result in range(plus_results):
                self.table.append(Dare(
                                        title=f'+ {int(time_result / 2) + 1} Min Skin Pro',
                                        description=f'+ {int(time_result / 2) + 1} Min Skin Pro',
                                        level=self.actual_level,
                                        dare_type=self.get_table_type_integer(),
                                        value=int(time_result / 2) + 1,
                                        action=1))

    def start_wheel(self, type_wheel):
        self.table_type = type_wheel
        if type_wheel == 'subscribe':
            self.image_wheel = image.load(f'assets/wheel_privacy.png').convert_alpha()
        else:
            self.image_wheel = image.load(f'assets/wheel_{type_wheel}.png').convert_alpha()
        self.table_results([])
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

    def start_bar(self, type_extractor, divisor, icon_location, bar_location):
        self.bar_foreground = resize(image.load('assets/bar_foreground.png').convert_alpha(), 0.5)
        self.bar_background = resize(image.load('assets/bar_background.png').convert_alpha(), 0.5)
        self.icon = resize(image.load(f'assets/{type_extractor}.png').convert_alpha(), 0.1 if divisor == 150 else 0.15)
        self.extract = Extractor(type_extractor)
        self.location = {'icon': icon_location,
                         'bar': bar_location}
        self.divisor = divisor
        self.level_icon = resize(image.load(f'assets/level.png').convert_alpha(), 0.25)

    def get_last_amount_string(self):
        return f'Faltam: {self.divisor - (self.like_to_show % self.divisor)} {self.table_type}'

    def draw_bar(self, game):
        cost_surface = game.font_info.render(self.get_last_amount_string(), True, (255, 255, 0))
        position_cost_text = (self.location['bar'][0] + 300, self.location['bar'][1] - 20)
        game.screen.blit(cost_surface, position_cost_text)

        position_cost_text = (550, self.location['bar'][1] - 14)
        game.screen.blit(self.level_icon, position_cost_text)
        cost_surface = game.font_info.render(str(self.actual_level), True, (0, 0, 0))
        position_cost_text = (570, self.location['bar'][1])
        game.screen.blit(resize(cost_surface, 1.4), position_cost_text)

        game.screen.blit(self.icon, self.location['icon'])
        game.screen.blit(self.bar_background, self.location['bar'])
        draw.rect(game.screen,
                  Color(255, 0, 0),
                  Rect(self.location['bar'][0] + 8, self.location['bar'][1] + 8,
                       455 * (self.like_to_show / self.divisor), 7))

        if self.actual_level < len(self.level_grid):
            draw.rect(game.screen,
                      Color(255, 255, 0),
                      Rect(self.location['bar'][0] + 8, self.location['bar'][1] + 15, 455 * (
                                  (self.xp_points - self.level_grid[self.actual_level - 1]) / self.level_grid[
                              self.actual_level]), 7))
        else:
            draw.rect(game.screen,
                      Color(255, 255, 0),
                      Rect(self.location['bar'][0] + 8, self.location['bar'][1] + 15, 455, 7))
        game.screen.blit(self.bar_foreground, self.location['bar'])


class Like(Wheel, Bar):
    def __init__(self):
        super().__init__()
        self.start_bar('likes', 5000, (15, 40), (70, 50))
        self.start_wheel('likes')
        self.next_extract = datetime.now()

    def update(self, game):
        if self.next_extract <= datetime.now():
            actual_like_count = self.extract.get_value()
            game.like_left_to_show += actual_like_count - self.like_amount
            self.like_to_show += actual_like_count - self.like_amount
            self.like_amount = actual_like_count
            self.xp_points = self.like_amount * 10
            self.spin_wheel()
            self.next_extract += timedelta(seconds=10)
        self.get_new_level()
        self.draw_bar(game)

    def validate_extract(self):
        response = False
        if self.next_extract <= datetime.now():
            response = self.extract.is_possible_extract()
            self.next_extract += timedelta(seconds=10)
        return response


class Gift(Wheel, Bar):
    def __init__(self):
        super().__init__()
        self.start_bar('coins', 150, (15, 120), (70, 130))
        self.start_wheel('coins')
        self.next_extract = datetime.now()
        # self.sub_extractor = Extractor('subs')
        # self.sub_name_extractor = Extractor('name')

    def update(self, game):
        if self.next_extract <= datetime.now():
            actual_like_count = self.extract.get_value()
            game.coins_left_to_show += actual_like_count - self.like_amount
            self.like_to_show += actual_like_count - self.like_amount
            self.like_amount = actual_like_count
            self.xp_points = self.like_amount * 10
            # self.get_sub_name_(game)
            # self.get_sub_name(game)
            self.spin_wheel()
            self.next_extract += timedelta(seconds=10)
        self.get_new_level()
        self.draw_bar(game)

    # def get_sub_spin(self):
    #     cloud_subs = self.sub_extractor.get_value()
    #     while cloud_subs > self.sub_amount:
    #         self.spin += 1
    #         self.sub_spinning += 1
    #         self.sub_amount += 1
    #     self.get_sub_name()

    # def get_sub_name(self, game):
    #     new_subscriber = self.sub_name_extractor.get_sub_name()
    #     if new_subscriber and new_subscriber not in game.all_new_subscribers:
    #         game.all_new_subscribers.append(new_subscriber)
    #         self.spin += 1
    #         self.subscriber_name_list.append(new_subscriber)
    #
    # def get_sub_name_(self, game):
    #     webhook_list = Webhook.select().where(Webhook.updated_at.is_null())
    #     for new_webhook in webhook_list:
    #         webhook_json = json.loads(new_webhook.raw_data)
    #         try:
    #             if webhook_json['resource']['type'] == "subscription" and webhook_json['event'] == "new":
    #                 new_subscriber = str(new_webhook.webhook_id)
    #                 game.all_new_subscribers.append(new_subscriber)
    #                 self.spin += 1
    #                 self.subscriber_name_list.append(new_subscriber)
    #             new_webhook.updated_at = datetime.now()
    #             new_webhook.save()
    #         except Exception as e:
    #             new_webhook.updated_at = datetime.now()
    #             new_webhook.save()

    def validate_extract(self):
        response = False
        if self.next_extract <= datetime.now():
            response = self.extract.is_possible_extract()
            self.next_extract += timedelta(seconds=10)
        return response


class Subscribe(Wheel):
    def __init__(self):
        super().__init__()
        self.start_wheel('subscribe')
        self.next_extract = datetime.now()
        self.next_privvacy_extract = datetime.now()
        self.sub_extractor = Extractor('subs')
        self.sub_name_extractor = Extractor('name')
        self.id_privacy = 1
        self.actual_level = 4

    def update(self, game):
        if self.next_privvacy_extract <= datetime.now():
            self.get_privacy_sub(game)
            self.id_privacy += 1
            self.spin_wheel()
            self.next_privvacy_extract += timedelta(minutes=2)

        if self.next_extract <= datetime.now():
            self.get_livepix_sub(game)
            self.get_tiktok_sub(game)
            self.spin_wheel()
            self.next_extract += timedelta(seconds=10)
        self.get_new_level()

    def get_tiktok_sub(self, game):
        new_subscriber = self.sub_name_extractor.get_sub_name()
        if new_subscriber and new_subscriber not in game.all_new_subscribers:
            game.all_new_subscribers.append(new_subscriber)
            self.spin += 1
            self.subscriber_name_list.append(new_subscriber)

    def get_livepix_sub(self, game):
        webhook_list = Webhook.select().where(Webhook.updated_at.is_null())
        for new_webhook in webhook_list:
            webhook_json = json.loads(new_webhook.raw_data)
            try:
                if webhook_json['resource']['type'] == "subscription" and webhook_json['event'] == "new":
                    new_subscriber = str(new_webhook.webhook_id)
                    game.all_new_subscribers.append(new_subscriber)
                    self.spin += 1
                    self.subscriber_name_list.append(new_subscriber)
                new_webhook.updated_at = datetime.now()
                new_webhook.save()
            except Exception as e:
                new_webhook.updated_at = datetime.now()
                new_webhook.save()

    def get_privacy_sub(self, game):
        how_many_spins = get_privacy_sell()
        new_subscriber = 'Superfã PRIVACY ' + str(self.id_privacy)
        if new_subscriber and new_subscriber not in game.all_new_subscribers:
            game.all_new_subscribers.append(new_subscriber)
            self.spin += how_many_spins
            self.subscriber_name_list.append(new_subscriber)

    def spin_wheel(self):
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


class Word:

    def __init__(self, word, map_to_reveal):
        self.word = word
        self.revealed = ["_"] * len(self.word)
        self.next_to_reveal = 0
        self.map_to_reveal = []
        self.get_map(map_to_reveal)
        self.how_many_reveal = len(self.map_to_reveal)

    def reveal_next(self):
        self.revealed[self.map_to_reveal[self.next_to_reveal]] = self.word[self.map_to_reveal[self.next_to_reveal]]
        self.next_to_reveal += 1

    def can_reveal(self):
        return self.next_to_reveal < self.how_many_reveal

    def get_map(self, map_to_reveal):
        for index in map_to_reveal.split(','):
            self.map_to_reveal.append(int(index))
        shuffle(self.map_to_reveal)


class WordGame:

    def __init__(self, time_reveal):
        self.word_list = []
        self.get_word_list_by_database()
        self.actual_word = None
        self.font = font.SysFont('Montserrat Heavy', 210, False)
        self.next_time_reveal = datetime.now()
        self.show_game = True
        self.time_reveal = time_reveal

    def get_word_list(self):
        with open('words.txt') as word_file:
            for raw_word in word_file:
                word, map_reveal = raw_word.split(';')
                self.word_list.append(Word(word, map_reveal))

    def get_word_list_by_database(self):
        for word_model in WordModel.get_all_words():
            self.word_list.append(Word(word_model.word, word_model.map_reveal))
            word_model.is_valid = False
            word_model.save()
        shuffle(self.word_list)

    def reveal(self):
        self.actual_word.revealed = self.actual_word.word

    def reveal_letter(self, letter):
        self.actual_word.reveal_letter(letter)

    def update(self, game):
        if self.show_game and self.actual_word and not game.next_spin:
            self.reveal_next_word()
            width_rect = 190
            height_rect = 360
            margin = 30
            start_x = (game.screen.get_width() - (len(self.actual_word.revealed) * (width_rect + margin) - margin)) // 2
            start_y = (game.screen.get_height() - height_rect) // 2
            for index, letter in enumerate(self.actual_word.revealed):
                x = start_x + index * (width_rect + margin)
                y = start_y + 60

                if index not in self.actual_word.map_to_reveal:
                    draw_gradient_rect(game.screen, (x, y, width_rect, height_rect), (255, 255, 255), (255, 0, 0))
                else:
                    draw_gradient_rect(game.screen, (x, y, width_rect, height_rect), (220, 220, 220), (255, 255, 255))
                draw.rect(game.screen, (0, 0, 0), (x, y, width_rect, height_rect), 3)

                if letter:
                    string_surface = self.font.render(letter.upper(), True, (0, 0, 0))
                    string_surface = resize_without_proportion(string_surface, 1, 2.2)
                    game.screen.blit(string_surface, (x + width_rect // 2 - string_surface.get_width() // 2,
                                                      y + height_rect // 2 - string_surface.get_height() // 2))

    def get_next_word(self):
        if self.word_list:
            self.next_time_reveal = datetime.now() + timedelta(seconds=self.time_reveal)
            self.actual_word = self.word_list.pop()
        else:
            self.actual_word = None

    def reveal_next_word(self):
        if datetime.now() >= self.next_time_reveal and self.actual_word.can_reveal():
            self.actual_word.reveal_next()
            self.next_time_reveal = datetime.now() + timedelta(seconds=self.time_reveal)

