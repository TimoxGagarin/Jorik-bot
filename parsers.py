import requests
import wikipedia
from random import randint
from bs4 import BeautifulSoup

WEATHER_URL = 'https://wttr.in'

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
              'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': '*/*',
    'Accept-Language': 'ru',
}

WEATHER_PARAMS = {
    'format': 2,
    '0': '',
    'T': '',
    'M': '',
}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def send_weather(city):
    try:
        if city is None:
            return 'введите в команду город!'
        html = get_html(f'{WEATHER_URL}/{city}', params=WEATHER_PARAMS)
        if html.status_code == 200:
            return f'погода на сегодня в городе {city}: \n {html.text}'
        else:
            return 'Ошибка на сервере погоды! Не могу дать ответ'
    except requests.ConnectionError:
        return 'Сетевая ошибка! Не могу дать ответ'


def send_description(name):
    try:
        wikipedia.set_lang("ru")
        page = f'{wikipedia.summary(name)}'
        return page
    except ApiError as err:
        if str(err).startswith('[914]'):
            return 'описание слишком длинное, перейдите по ссылке - {wikipedia.page(name).url}'
    except wikipedia.exceptions.PageError:
        return 'данная страница не найдена!'
    except wikipedia.exceptions.DisambiguationError as e:
        list_opt = '\r\n'.join(e.options)
        return f'что-то пошло не так. Возможно вы имели ввиду:\r\n{list_opt}'

    
def send_cats_urls():
    return 'http://thecatapi.com/api/images/get'
