from pygame import image, mixer
from image_utils import *
from os import listdir

PATH = './assets/'


class Image:
    def __init__(self, image_data):
        self.image_show = image_data


class ImageList:
    def __init__(self, path):
        self.image_list = []
        self.load_all_images(path)
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

    def load_all_images(self, path):
        for file in listdir(PATH + path):
            self.image_list.append(Image(fixed_resize_high_size(
                image.load(PATH + path + file).convert_alpha().convert_alpha(), 40)))


class HeartImage:
    def __init__(self, theme):
        self.images = ImageList(f'{theme}/like/')


class CoinImage:
    def __init__(self, theme):
        self.images = ImageList(f'{theme}/coin/')


class Assets:

    def __init__(self, theme):
        self.background = image.load(f'assets/{theme}/img.png').convert_alpha()
        self.qrcode = image.load('assets/qr_code.png').convert_alpha()
        self.result_board = image.load('assets/board_last_result.png').convert_alpha()
        self.cron_board = image.load('assets/cron.png').convert_alpha()

        self.heart_image = HeartImage(theme)
        self.coins_image = CoinImage(theme)

        self.podium_image = resize(image.load('assets/podio.png').convert_alpha(), 1.8)
        self.lush_image = image.load('assets/lush.png').convert_alpha()

        self.gift_image = resize(image.load('assets/coins.png').convert_alpha(), 0.08)
        self.like_image = resize(image.load('assets/likes.png').convert_alpha(), 0.15)
        self.sub_image = resize(image.load('assets/sub.png').convert_alpha(), 0.15)

        self.border_wheel = image.load(f'assets/{theme}/borda.png').convert_alpha()
        self.table = image.load('assets/tabela.png').convert_alpha()
        self.sup_line = image.load('assets/sup_line.png').convert_alpha()
        self.sup_line_spin = image.load('assets/sup_line_spin.png').convert_alpha()
        self.bottom_line = image.load('assets/botton_line.png').convert_alpha()
        self.sup_line_top_liker = resize(image.load('assets/sup_line_top_liker.png').convert_alpha(), 1.8)
        self.sup_line_top_gifter = resize(image.load('assets/sup_line_top_gifter.png').convert_alpha(), 1.8)

        self.wheel_sound = mixer.Sound('assets/click.mp3')
        self.end_time_song = mixer.Sound('assets/ding.mp3')
        self.sub_song = mixer.Sound('assets/sub.mp3')

