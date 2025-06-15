from pygame import image, transform
from image_utils import resize
from datetime import datetime, timedelta


ATK = 15
DEF = 15


class Club:
    def __init__(self, name: str):
        self.club_name = name
        self.escudo = resize(image.load(f"assets/times/{name.replace(' ', '').lower()}.png").convert_alpha(), 0.35)
        self.escudo_icon = resize(image.load(f"assets/times/{name.replace(' ', '').lower()}.png").convert_alpha(), 0.1)
        self.escudo_scoreboard = resize(image.load(f"assets/times/{name.replace(' ', '').lower()}.png").convert_alpha(),
                                        0.13)
        self.crowd_scream = 0
        self.goal = 0
        self.var_chance = 0.05
        self.goal_chance = 0.1
        self.time_atk = timedelta(seconds=ATK)
        self.time_def = timedelta(seconds=DEF)
        self.end_act = None

    def plus_time_atk(self, time):
        if self.time_atk + time <= timedelta(seconds=50):
            self.time_atk += time
        else:
            self.time_atk = timedelta(seconds=50)

    def plus_time_def(self, time):
        if self.time_def + time <= timedelta(seconds=50):
            self.time_def += time
        else:
            self.time_def = timedelta(seconds=50)

    def plus_goal(self):
        self.goal += 1
        self.goal_chance = 0.1

    def plus_var_chance(self, var_chance):
        if self.var_chance + var_chance <= 0.5:
            self.var_chance += var_chance
        else:
            self.var_chance = 0.5

    def plus_goal_chance(self, goal_chance):
        if self.goal_chance + goal_chance <= 0.3:
            self.goal_chance += goal_chance
        else:
            self.goal_chance = 0.3

    def restart(self):
        self.goal = 0
        self.var_chance = 0.05
        self.goal_chance = 0.1
        self.time_atk = timedelta(seconds=ATK)
        self.time_def = timedelta(seconds=DEF)
        self.end_act = None


class Goalkeeper:

    def __init__(self):
        self.idle = image.load('assets/times/goleiro_idle.png').convert_alpha()
        self.def_right = image.load('assets/times/goleiro.png').convert_alpha()
        self.def_left = transform.flip(self.def_right, False, True)


class LoadFiles:

    def __init__(self, club_list):
        self.background = image.load('assets/times/background.png').convert_alpha()
        self.qrcode = image.load('assets/qr_code.png').convert_alpha()
        self.result_board = image.load('assets/board_last_result.png').convert_alpha()
        self.cron_board = image.load('assets/cron.png').convert_alpha()
        self.heart_image = image.load('assets/heart.png').convert_alpha()
        self.coins_image = image.load('assets/coins_gift.png').convert_alpha()
        self.sharing_image = image.load('assets/sharing.png').convert_alpha()
        self.podium_image = image.load('assets/podio.png').convert_alpha()
        self.gift_image = resize(image.load('assets/coins.png').convert_alpha(), 0.08)
        self.like_image = resize(image.load('assets/likes.png').convert_alpha(), 0.12)
        self.share_image = resize(image.load('assets/shares.png').convert_alpha(), 0.03)
        self.border_wheel = image.load('assets/borda.png').convert_alpha()
        self.flanelinha = image.load('assets/flanelinha.png').convert_alpha()
        self.table = image.load('assets/tabela.png').convert_alpha()
        self.sup_line = image.load('assets/sup_line.png').convert_alpha()
        self.sup_line_spin = image.load('assets/sup_line_spin.png').convert_alpha()
        self.bottom_line = image.load('assets/botton_line.png').convert_alpha()
        self.sup_line_top_liker = image.load('assets/sup_line_top_liker.png').convert_alpha()
        self.sup_line_top_gifter = image.load('assets/sup_line_top_gifter.png').convert_alpha()
        self.sup_line_time_skin = image.load('assets/sup_line_top_skin.png').convert_alpha()
        self.ball = image.load('assets/times/bola.png').convert_alpha()
        self.scoreboard = resize(image.load('assets/times/placar.png').convert_alpha(), 1.3)
        self.var_board = image.load('assets/times/var.png').convert_alpha()
        self.goal = image.load('assets/times/goal.png').convert_alpha()
        self.goalkeeper = Goalkeeper()
        self.club_dict = {}
        self.club_list = []
        self.get_clubs(club_list)

    def get_clubs(self, club_list):
        for club_name in club_list:
            club = Club(club_name)
            self.club_dict[club_name] = club
            self.club_list.append(club)


