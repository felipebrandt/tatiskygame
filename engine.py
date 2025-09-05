from extract import *
from image_utils import resize
from pygame import image, draw, Color, Rect
from pygame.sprite import Sprite
from datetime import datetime
from random import randint, shuffle
from models import Webhook
import json
from imap import get_privacy_sell


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
                self.table_results()

    @staticmethod
    def remove_last_results(results, table):
        if results:
            for result in results:
                if result in table:
                    table.remove(result)
        return table

    def table_results(self, result_list=None):

        if self.table_type == 'coins':
            tatisky = [Effect('+1 Min Skin Pro', 1), Effect('+1 Min Skin Pro', 1),
                       Effect('+2 Min Skin Pro', 2), Effect('+2 Min Skin Pro', 2),
                       Effect('+3 Min Skin Pro', 3), Effect('+4 Min Skin Pro', 4)]
        elif self.table_type == 'shares':
            tatisky = [Effect('Carinho', 0), Effect('Troca a Skin', 0), Effect('Fica de Pé', 0),
                       Effect( 'Dança Gatinha', 0), Effect('Mostra o Look', 0), Effect('Dança na Cadeira', 0)]
        else:
            tatisky = [Effect('Manda um Beijo', 0), Effect('Faz um Brinde', 0),
                       Effect('Desfila', 0), Effect('Faz Pose', 0)]

        light_like_result = ['Mostra o Look', 'Mandar Beijinho', 'Mandar MiniCoração', 'Fazer um Brinde', 'Desenha no Quadro', 'Fazer Careta', 'Imita Um Personagem', 'Desafina na Musica', 'Fazer Pose', 'Finge Tocar Instrumento']
        medium_like_result = ['Rebola na Cadeira', 'Dança na Cadeira', 'Desfilar na Passarela', 'Mostra a Raba', 'Fantasia de Professora', 'Faz Cara de Safada', 'Pintada na Coxa', 'Ensina Professora', 'Conta Segredo']
        hard_like_result = ['Ajeita a Flanelinha', 'Carinho Por Cima', 'Carinho Por Dentro', 'Carinho Em Volta', 'Contar um Segredo', 'Dança na Camera', 'Mostra a Pintinha', 'Carinho na Coxa']

        light_gift_result = ['Mostra a Raba', 'Fazer Pose', 'Rebola na Cadeira', 'Faz Cara de Safada', 'Carinho Por Cima', 'Pintada na Coxa']
        medium_gift_result = ['Rebola na Camera', 'Mostra a Pintinha', 'Ajeita a Flanelinha', 'Dança na Camera', 'Carinho na Coxa']
        hard_gift_result = ['Carinho Por Dentro', 'Molha o Dedinho', 'Agaixadinha na Camera', 'Carinho Em Volta']

        light_like_result = self.remove_last_results(result_list, light_like_result)
        medium_like_result = self.remove_last_results(result_list, medium_like_result)
        hard_like_result = self.remove_last_results(result_list, hard_like_result)
        shuffle(light_gift_result)
        shuffle(medium_like_result)
        shuffle(hard_like_result)

        light_gift_result = self.remove_last_results(result_list, light_gift_result)
        medium_gift_result = self.remove_last_results(result_list, medium_gift_result)
        hard_gift_result = self.remove_last_results(result_list, hard_gift_result)
        shuffle(light_like_result)
        shuffle(medium_gift_result)
        shuffle(hard_gift_result)

        like_table = {1: [7, 3, 2],
                      2: [6, 3, 2],
                      3: [6, 4, 2],
                      4: [5, 4, 3],
                      5: [4, 5, 3],
                      6: [4, 4, 4],
                      7: [3, 6, 3],
                      8: [3, 5, 4],
                      9: [2, 5, 5],
                      10: [1, 5, 6]}

        gift_table = {1: [5, 4, 0],
                      2: [4, 4, 0],
                      3: [3, 3, 1],
                      4: [2, 3, 2],
                      5: [1, 3, 3],
                      6: [1, 2, 3],
                      7: [0, 3, 3],
                      8: [0, 2, 3],
                      9: [0, 1, 3],
                      10: [0, 0, 3]}

        sub_table = {1: [0, 3, 3],
                      2: [0, 3, 3],
                      3: [0, 3, 3],
                      4: [0, 3, 3],
                      5: [0, 3, 3],
                      6: [0, 3, 3],
                      7: [0, 3, 3],
                      8: [0, 3, 3],
                      9: [0, 3, 3],
                      10: [0, 3, 3]}

        low, midi, high = like_table[self.actual_level]
        low_level = light_like_result[:low]
        mid_level = medium_like_result[:midi]
        high_level = hard_like_result[:high]

        like_results = low_level + mid_level + high_level

        low, midi, high = gift_table[self.actual_level]
        low_level = light_gift_result[:low]
        mid_level = medium_gift_result[:midi]
        high_level = hard_gift_result[:high]

        gift_results = low_level + mid_level + high_level

        # low_level = light_like_result + light_like_result
        # for i in range(like_table[self.actual_level][0]):
        #     like_results.append(low_level[i])
        # mid_level = medium_like_result + medium_like_result
        # for i in range(like_table[self.actual_level][1]):
        #     like_results.append(mid_level[i])
        # high_level = hard_like_result + hard_like_result
        # for i in range(like_table[self.actual_level][2]):
        #     like_results.append(high_level[i])
        #
        # low_level = light_like_result + light_like_result
        # for i in range(like_table[self.actual_level][0]):
        #     like_results.append(low_level[i])
        # mid_level = medium_like_result + medium_like_result
        # for i in range(like_table[self.actual_level][1]):
        #     like_results.append(mid_level[i])
        # high_level = hard_like_result + hard_like_result
        # for i in range(like_table[self.actual_level][2]):
        #     like_results.append(high_level[i])
        #
        # type_result = 0
        # for result in gift_table[self.actual_level]:
        #     if type_result == 0:
        #         low_level = light_gift_result + light_gift_result
        #         for i in range(result):
        #             gift_results.append(low_level[i])
        #     if type_result == 1:
        #         mid_level = medium_gift_result + medium_gift_result
        #         for i in range(result):
        #             gift_results.append(mid_level[i])
        #     if type_result == 2:
        #         high_level = hard_gift_result + hard_gift_result
        #         for i in range(result):
        #             gift_results.append(high_level[i])

        plus_results = 12 - len(gift_results)
        for time_result in range(plus_results):
            gift_results.append(f'+ {int(time_result/2) + 1} Min Transparente')

        self.table = like_results if self.table_type == 'likes' else gift_results

    def start_wheel(self, type_wheel):
        self.table_type = type_wheel
        if type_wheel == 'subscribe':
            self.image_wheel = image.load(f'assets/wheel_privacy.png').convert_alpha()
        else:
            self.image_wheel = image.load(f'assets/wheel_{type_wheel}.png').convert_alpha()
        self.table_results()
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


if __name__ == '__main__':
    gift = Gift()
    gift.get_sub_name_()


