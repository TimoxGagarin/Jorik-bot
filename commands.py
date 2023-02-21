import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.exceptions import ApiError
from random import randint
from config import temp_texts, mailing, CHAT_ID, GROUP_ID
from Message import Message
from UseDatabase import *
from parsers import *
import datetime as dt
from threading import Thread, Timer, enumerate
import emoji as moji
import time
import sys
from io import BytesIO
import requests
from vk_funcs import *
from vk_info import *


# send sticker with id
def sticker(message):
    num = message.text_low.replace('стикер ', '').strip()
    try:
        send_stick(message.text_low.replace('стикер ', '').strip())
    except ApiError:
        sender('Такого стикера не существует!')


def infa(to):
    sender(f'{to}, вероятность этого составляет {randint(1, 100)}%')


def who(message, to):
    man = message.items[randint(2, len(message.items)) - 1]
    user_id = vk.users.get(user_ids=man['member_id'])[0]['id']
    info = message.text.replace('кто ', '')
    sender(f'{to}, {info} - {get_name(user_id)}')


def wheather(message, to):
    city = message.text[7:]
    sender(f'{to}, {send_weather(city)}')


def what_it_is(message, to):
    name = message.text[10:]
    sender(f'{to}, {send_description(name)}')


def marry_command(message, to):
    if check_marriage(user_id=message.user_id) != '':
        sender(f'{to}, вы уже состоите в браке. Сначала разведитесь.')
        return
    wife_name = message.text[5:]
    wife_id = get_id(wife_name, message.event)
    husband_id = message.user_id
    wife_name = name_or_nick(wife_id)
    if wife_id == husband_id:
        sender(f'{to}, нельзя заключить брак с самим собой')
        return
    if check_marriage(user_id=wife_id) != '':
        sender(f'{to}, {wife_name} уже состоит в браке.')
        return

    def create_keyboard():
        keyboard = vk_api.keyboard.VkKeyboard(one_time=False)
        keyboard.add_button("Да", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
        keyboard.add_button("Нет", color=vk_api.keyboard.VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    sender(f'Согласен(на) ли {wife_name} стать мужем(женой) {to}?', keyboard=create_keyboard())

    def get_agreement(id1, id2):
        sender(f'{to}, время на согласие вышло. Повторите отправку команды позже.')
        return id1, id2

    def check_marriage_request(agreement, husband_id, wife_id):
        while agreement is not None:
            if agreement.is_alive():
                husband = name_or_nick(husband_id)
                wife = name_or_nick(wife_id)
                if message.user_id == wife_id:
                    if message.text_low == f'{group_name_anchor()} да':
                        marry(user_id1=husband_id, user_id2=wife_id)
                        sender(f'💍🤵👰 Поздравим {husband} и {wife} с заключением брака!')
                        agreement.cancel()
                        wife_id = None
                        husband_id = None
                    elif message.text_low == f'{group_name_anchor()} нет':
                        sender(f'{husband}, {wife} отверг(ла) ваше предложение.')
                        agreement.cancel()
                        wife_id = None
                        husband_id = None

    agreement = Timer(30, get_agreement, [husband_id, wife_id])
    agreement.start()
    check_marriage_thread = Thread(target=check_marriage_request, args=[agreement, husband_id, wife_id])
    check_marriage_thread.start()

def divorce_command(message, to):
    partners = check_marriage(user_id=message.user_id).split('_')
    if partners is []:
        sender(f'{to}, вы не состоите в браке.')
        return
    husband = name_or_nick(partners[0])
    wife = name_or_nick(partners[1])
    divorce(user_id=message.user_id)
    if husband == to:
        sender(f'{to} расторг брак c {wife}')
    else:
        sender(f'{to} расторг брак c {husband}')


def commands_list():
    text = moji.emojize(':memo: Список команд:\n')
    commands_list = list()
    [commands_list.append(f'{k} - {v}\n') for k, v in commands.items()]
    sender(text + ''.join(commands_list))


def statuses_list():
    users_statuses = statuses()

    def get_key(users_statuses, value):
        keys = list()
        [keys.append(user_id) if status == value else None for user_id, status in users_statuses.items()]
        return keys

    def get_names(user_ids):
        users_names_list = list()
        [users_names_list.append(name_or_nick(user_id)) for user_id in user_ids]
        user_names_str = '\n'.join(users_names_list)
        return user_names_str

    text = moji.emojize(":memo: Статусы пользователей беседы:\n")
    for i in range(1, 5):
        if len(get_names(get_key(users_statuses, 6 - i))) > 0:
            text += f"\n{temp_texts[f'STATUS{6 - i}']} ({6 - i}):\n{get_names(get_key(users_statuses, 6 - i))}\n"
    sender(text)


def nicks_list():
    def get_names():
        users_names_list = list()
        i = 0
        for user_id, nick in nicks().items():
            if (nick is None or nick.strip() == '') or nick.split('|')[1] == ']':
                continue
            else:
                i += 1
                users_names_list.append(
                    f"{i}. {name_or_nick(user_id)} - {get_name(user_id) + ' ' + get_surname(user_id)}")
        user_names_str = '\n'.join(users_names_list)
        return "Ников нету" if user_names_str.strip() == '' else user_names_str

    sender(moji.emojize(f":memo: Ники пользователей:\n\n{get_names()}"))


def marriages_list():
    marriages = list(check_marriages())

    def get_marriages():
        marriages_list = list()
        for i in range(0, len(marriages)):
            marriage_info = marriages[i].split('_')
            husband = name_or_nick(marriage_info[0])
            wife = name_or_nick(marriage_info[1])
            marriage_time = (dt.datetime.now() - dt.datetime.strptime(marriage_info[2], '%d.%m.%Y')).days
            marriages_list.append(f"{i + 1}. {husband} и {wife} ({marriage_time} дн.)")
        marriages_str = '\n'.join(marriages_list)
        return "Браков нету" if marriages_str.strip() == '' else marriages_str

    sender(moji.emojize(f":memo: Браки пользователей:\n\n{get_marriages()}"))


def preds_list():
    def get_preds():
        users_names_list = list()
        i = 0
        for user_id, preds_count in preds().items():
            if preds_count is None or preds_count == 0:
                continue
            else:
                i += 1
                users_names_list.append(f"{i}. {name_or_nick(user_id)} ({preds_count}/5)")
        user_names_str = '\n'.join(users_names_list)
        return "Предупреждений нету" if user_names_str.strip() == '' else user_names_str

    sender(moji.emojize(f":memo: Предупреждения пользователей:\n\n{get_preds()}"))


def ban_phrase(message, to):
    bad_word = message.text_low[14:]
    with open('Bad_words.txt', 'a') as file:
        file.write(f'\n{bad_word}')
    bad_words.add(bad_word)
    sender(f'{to}, данная фраза добавлена в список запрещенных.')


def unban_phrase(message, to):
    bad_word = message.text_low[14:]
    if bad_word in bad_words:
        bad_words.remove(bad_word)
        with open('Bad_words.txt', 'w') as file:
            [file.write(f'{line}\n') for line in bad_words]
        sender(f'{to}, данная фраза убрана из списка запрещенных')
    else:
        sender(f'{to}, данная фраза отсутствует в списке запрещенных')


def bad_words_list():
    sender(f'Запрещенные фразы: {", ".join([f"{word.title()}" for word in bad_words])}')


def new_greeting(message, to):
    temp_texts['WELCOMING'] = message.text[18:].strip()
    render_new_temps()
    sender(f'{to}, новое приветствие установлено!')


def new_byeing(message, to):
    temp_texts['BYEBYING'] = message.text[15:].strip()
    render_new_temps()
    sender(f'{to}, новое прощание установлено!')


def new_kick_text(message, to):
    temp_texts['KICK_TEXT'] = message.text[17:].strip()
    render_new_temps()
    sender(f'{to}, новый текст кика установлен!')


def give_status(message, to):
    status = message.text[7:8].strip()
    try:
        if int(message.status) < int(status):
            sender(f'{to}, отказано в доступе ({check_status(user_id=message.user_id)}<={status})')
            return
        user_id = get_id(message.text[9:].strip(), message.event)
        user_name = name_or_nick(user_id)
        if user_name == "Участника с таким именем не существует":
            sender(f'{to}, участника с таким именем не существует!')
            return
        set_status(user_id=user_id, status=int(status))
        sender(f'{to}, {user_name} был установлен статус {status}!')
    except ValueError:
        sender(f'{to}, некорректный ввод команды')


def kick(message, to):
    user_id = get_id(message.text[4:].strip(), message.event)
    user_status = check_status(user_id=user_id)
    if user_status and user_status >= message.status:
        sender(f'{to}, отказано в доступе ({message.status}<={user_status})')
        return
    kick_user(user_id)


def pred(message, to):
    user_id = get_id(message.text[5:].strip(), message.event)
    user_name = name_or_nick(user_id)
    user_status = check_status(user_id=user_id)
    if user_status and user_status >= message.status:
        sender(f'{to}, отказано в доступе ({message.status}<={user_status})')
        return
    if user_name == "Участника с таким именем не существует":
        sender(f'{to}, участника с таким именем не существует!')
        return
    add_pred_and_check(user_id)


def remove_pred(message, to):
    user_id = get_id(message.text[11:].strip(), message.event)
    user_name = name_or_nick(user_id)
    user_status = check_status(user_id=user_id)
    if user_status and user_status >= message.status:
        sender(f'{to}, отказано в доступе ({message.status}<={user_status})')
        return
    if user_name == "Участника с таким именем не существует":
        sender(f'{to}, участника с таким именем не существует!')
        return
    sender(f"У {user_name} было снято 1 предупреждение.")
    remove_pred_db(user_id=user_id)


def reload_all(message, to):
    reg_all(message.event)
    reload_admins(message.event)
    sender(f'{to}, администраторы беседы обновились')


def give_nick(message, to):
    nick = message.text[8:].strip()
    set_nick(user_id=message.user_id, nick=nick)
    sender(f'Пользователю {to} был установлен ник {nick}!')


def send_cat(to):
    sender(f'{to}, держи котика', photo=send_cats_urls())


def mailing_set(message, to):
    global mailing
    state = message.text_low[9:].strip()
    if state == 'on':
        mailing = True
        sender(f'{to}, рассылка включена')
    elif state == 'off':
        mailing = False
        sender(f'{to}, рассылка отключена')
