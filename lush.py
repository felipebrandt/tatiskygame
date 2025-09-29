import requests
from random import randint


class Lush:

    def __init__(self, config):
        self.lush_api_key = config.lush_api_key
        self.lush_url = config.lush_url

    @staticmethod
    def get_intense(intense):
        if intense == 'Forte':
            return randint(13, 20)
        if intense == 'Médio':
            return randint(8, 12)
        if intense == 'Fraco':
            return randint(3, 7)

    def vibrate(self, time, intense):
        try:
            payload = {
                "command": "Function",
                "action": f"Vibrate:{intense}",
                "toy": "eedd6e7e84c5",
                "timeSec": time
            }
            headers = {
                "Authorization": self.lush_api_key,

                "Content-Type": "application/json"
            }
            requests.post(self.lush_url, json=payload, headers=headers)
        except Exception as e:
            print(f'Problema ao conectar a API: {e}')
        return None

