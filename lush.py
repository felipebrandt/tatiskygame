import requests
from random import randint
from models import Config


config = Config.select().get()

url = config.lush_url


def get_intense(intense):
    if intense == 'Forte':
        return randint(13, 20)
    if intense == 'Médio':
        return randint(8, 12)
    if intense == 'Fraco':
        return randint(3, 7)


def vibrate(time, intense):
    try:
        payload = {
            "command": "Function",
            "action": f"Vibrate:{intense}",
            "toy": "eedd6e7e84c5",
            "timeSec": time
        }
        headers = {
            "Authorization": config.lush_api_key,

            "Content-Type": "application/json"
        }
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f'Problema ao conectar a API: {e}')
    return None

