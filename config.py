main_token = input('Access token: ')
CHAT_ID = ''
GROUP_ID = input('Group id: ')

print('DB Config')
dbconfig = {'host': input('Host: '),
            'user': input('User: '),
            'password': input('Password: '),
            'database': input('Database name: '), }

commands = {
    'инфа ': 0,
    'кто ': 0,
    'стикер ': 0,
    'погода ': 0,
    'что такое ': 0,
    'статусы': 0,
    'команды': 0,
    'запрети фразу ': 5,
    'разреши фразу ': 5,
    'запрещенные фразы': 5,
    'новое приветствие:': 5,
    'новое прощание:': 5,
    'новый текст кика:': 5,
    'статус ': 5,
    'кик ': 4,
    'обновить': 0,
    'мне ник ': 1,
    'ники': 0,
    'преды': 0,
    'брак ': 0,
    'развод': 0,
    'браки': 0,
    'котик': 1,
    'пред ': 4,
    'снять пред ': 4,
    }

temp_texts = {
    'WELCOMING': 'Привет!',
    'BYEBYING': 'Пока(',
    'KICK_TEXT': 'Кышь мышь',
    'STATUS1': 'Активчик',
    'STATUS2': 'Элита',
    'STATUS3': 'Тестер',
    'STATUS4': 'Команда',
    'STATUS5': 'Лидер',
    'PREDS': 5,
}

mailing = True
