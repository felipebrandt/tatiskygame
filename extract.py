import time
from datetime import datetime, timedelta
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from io import BytesIO
from pygame import image, font
from image_utils import fixed_resize_width, fixed_resize_height


USER_ID = 1346265


class LoginTKinf:
    def __init__(self):
        options = Options()
        options.page_load_strategy = 'eager'
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)


class Extractor:

    def __init__(self, type_extractor):
        options = Options()
        options.page_load_strategy = 'eager'
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.type_extractor = type_extractor
        self.to_replace_tuple = self.get_replace_tuple()
        if type_extractor != 'name':
            self.driver.get(f'https://tikfinity.zerody.one/widget/goal?cid={USER_ID}&metric={self.type_extractor}')
        else:
            self.driver.get(f'https://tikfinity.zerody.one/widget/myactions?cid={USER_ID}&screen=1')
        time.sleep(5)

    def get_replace_tuple(self):
        if self.type_extractor == 'likes':
            return 'Like Goal - ', ' Likes'
        if self.type_extractor == 'coins':
            return 'Earned Coins - ', ' Coins'
        if self.type_extractor == 'subs':
            return 'Meta de Inscritos - ', ' Subs'

    def get_value(self):
        try:
            return int(
                self.driver.find_elements(By.CSS_SELECTOR, 'body > div > div > div.background.textContainer > div')[
                    0].text.replace(self.to_replace_tuple[0], '').replace(self.to_replace_tuple[1], '').split(' / ')[
                    0].replace('.', ''))
        except Exception as e:
            return 0

    def is_possible_extract(self):
        return False if \
        self.driver.find_elements(By.CSS_SELECTOR, 'body > div > div > div.background.textContainer > div')[
            0].text.find('No Data Available') >= 0 else True

    def get_sub_name(self):
        try:
            is_subscriber = self.driver.find_elements(By.CSS_SELECTOR, 'body > text.fadeIn > div:nth-child(2)')[0].text
            if is_subscriber and 'Inscrever' in is_subscriber:
                return self.driver.find_elements(By.CSS_SELECTOR, 'body > text.fadeIn > div.userHeader > div')[0].text
            return None
        except Exception as e:
            return None


MAX_STRING = 7


class RankedUser:

    def __init__(self, name, points, base64_image):
        self.name = self.string_to_pygame_image(self.truncate_string(name.split(' ')[0]), (255, 255, 255), 70)
        self.points = self.string_to_pygame_image(points, (230, 180, 240), 90)
        self.image = self.base64_to_pygame_image(base64_image)

    @staticmethod
    def base64_to_pygame_image(base64_image):
        return fixed_resize_width(image.load(BytesIO(base64_image)), 90)

    @staticmethod
    def string_to_pygame_image(string_value, color, size):
        font_used = font.SysFont('Montserrat Heavy', 25, False)
        string_surface = font_used.render(string_value, True, color)
        return fixed_resize_height(fixed_resize_width(string_surface, size), int(size/2))

    @staticmethod
    def truncate_string(string):
        if len(string) > MAX_STRING:
            return string[:MAX_STRING]
        return string


class Ranking:

    def __init__(self, top_type):
        options = Options()
        options.page_load_strategy = 'eager'
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.top_type = top_type
        self.driver.get(f'https://tikfinity.zerody.one/widget/top{top_type}?cid={USER_ID}')
        self.rank_list = []
        self.next_extract = datetime.now()
        time.sleep(5)

    def get_rank_list(self):
        try:
            rank_list = []
            url_ranked_list = self.driver.find_elements(By.CLASS_NAME, 'rankUser')
            while len(rank_list) < 3 and url_ranked_list:
                raw_user = url_ranked_list.pop(0)
                name, points = raw_user.text.split('\n')
                new_ranked_user = RankedUser(name, points, self.get_image(len(rank_list) + 1))
                rank_list.append(new_ranked_user)
            self.rank_list = rank_list
        except Exception as e:
            print(e)

    def get_image(self, next_rank):
        return self.driver.find_elements(By.CSS_SELECTOR, f'#rankingContainer > div:nth-child({next_rank}) > table > tbody > tr > td:nth-child(2) > img.profilePicture')[0].screenshot_as_png

    def update(self):
        if self.next_extract <= datetime.now():
            self.get_rank_list()
            self.next_extract += timedelta(seconds=10)


if __name__ == "__main__":
    new_rank = Ranking('gifter')
    new_rank.get_rank_list()
