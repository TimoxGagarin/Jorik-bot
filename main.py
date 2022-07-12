import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.exceptions import ApiError
from random import randint
from config import main_token, commands, temp_texts, mailing, CHAT_ID, GROUP_ID
from Message import Message
from UseDatabase import register, check_status, set_status, statuses, remove_from_db, check_nick, nicks, set_nick,\
    check_preds, preds, add_pred, remove_pred, marry, divorce, check_marriages, check_marriage
from parsers import send_weather, send_description, send_cats_urls
import datetime as dt
from threading import Thread, Timer
import emoji as moji
from io import BytesIO
import requests

EMPTY_KEYBOARD = VkKeyboard.get_empty_keyboard()


# get name in VK
def get_name(user_id):
    try:
        return f"[id{user_id}|{vk.users.get(user_ids = user_id)[0]['first_name']}]"
    except IndexError:
        return "Участника с таким именем не существует"


# get surname in VK
def get_surname(user_id):
    try:
        return f"[id{user_id}|{vk.users.get(user_ids = user_id)[0]['last_name']}]"
    except IndexError:
        return "Участника с таким именем не существует"


# Choose VK-name or nick
def name_or_nick(user_id):
    to = get_name(user_id)
    if check_nick(user_id):
        if check_nick(user_id).split('|')[1] != ']':
            to = check_nick(user_id)
    return to

    
# Function have rendering bad words from the file
def render_bad_words():
    with open('Bad_words.txt', 'r') as file:
        [bad_words.add(line.replace('\n', '')) for line in file]


# Function have rendering temps from the file
def render_temps():
    with open('temp_texts.txt', 'r') as file:
        for line in file:
            try:
                temp = line.split(':')[0]
                temp_texts[temp] = moji.emojize(line[len(temp) + 1:]).replace('\n', '')
            except Exception:
                pass


# Function have rendering temp to temps file
def render_new_temps():
    with open('temp_texts.txt', 'w') as file:
        try:
            [file.write(str(f'{k}: {moji.demojize(v)}\n')) for k, v in temp_texts.items()]
        except TypeError:
            pass

                
# Function check admin permissions
def reload_admins(event):
    people_items = vk_session.method('messages.getConversationMembers', {'peer_id': event.peer_id})['items']
    for member in people_items:
        try:
            if member['member_id'] < 0:
                continue
            if member['is_admin']:
                set_status(member['member_id'], 5)
                continue
        except KeyError:
            if check_status(member['member_id']) == 5:
                set_status(member['member_id'], 0)
                continue


def reg_all(event):
    members = vk_session.method('messages.getConversationMembers', {'peer_id': event.peer_id})['profiles']
    [register(member['id']) for member in members]


def get_id(name, event) -> bool:
    people_profiles = vk_session.method('messages.getConversationMembers', {'peer_id': event.peer_id})['profiles']
    for member in people_profiles:
        if((member['last_name'] == name)
           or (member['first_name'] == name) or (member['first_name'] + ' ' + member['last_name'] == name))\
                or str(member['id']) == str(name.split('|')[0].replace('[id', '')):
            return member['id']


# Function send text message
def sender(text='', keyboard=EMPTY_KEYBOARD, photo=None, wall_post='None'):
    post = {
        'chat_id': CHAT_ID,
        'random_id': 0,
        'keyboard': keyboard
    }        
    if text != '':
        post['message'] = text
    if wall_post != '':
        post['attachment'] = wall_post
    if photo is not None:
        img = requests.get(photo).content
        f = BytesIO(img) 
        photo_info = upload_photo(f)
        attachment = f'photo{photo_info[0]}_{photo_info[1]}_{photo_info[2]}'
        post['attachment'] = attachment
        
    vk_session.method('messages.send', post)
    

# Function send sticker from getting number
def send_stick(number):
    vk_session.method('messages.send', {'chat_id': message.chat_id, 'sticker_id': number, 'random_id': 0})


# Functions send photo
def upload_photo(photo):    
    response = upload.photo_messages(photo)[0]
    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']
    return owner_id, photo_id, access_key


# Function kick user from the chat
def kick_user(user_id):
    remove_from_db(user_id)
    vk_session.method('messages.removeChatUser', {'chat_id': message.chat_id, 'user_id': user_id, 'random_id': 0})


def add_pred_and_check(user_id):
    add_pred(user_id)
    to = name_or_nick(user_id)
    sender(f'{to} получает предупреждение ({check_preds(user_id)}/{temp_texts["PREDS"]})')
    if check_preds(user_id) == temp_texts['PREDS']:
        kick_user(user_id)


# Function have checking target of message
def for_jorik() -> bool:
    return message.text_low.startswith('жорик,')


# check your status and status of command
def compare_statuses(comm):
    if commands[comm] > message.status:
        sender(f'{message.name}, отказано в доступе ({message.status}<{commands[comm]})')
        return False
    return True


# check status and start of the message for [command]
def this_command(command) -> bool:
    return message.text_low.startswith(command) and compare_statuses(command)


def new_thread(func, args=None):
    if args is None:
        args = []
    stream = Thread(target=func, args=args)
    stream.start()
    stream.join()


# Function kick user if he wrote bad word from the list
def check_msg4bad_words():
    if message.status < 4:
        [add_pred_and_check(message.user_id) if word in bad_words else None for word in message.text_low.split(' ')]


############################
# Request processing funcs #
############################


# send sticker with id
def sticker():
    num = message.text_low.replace('стикер ', '').strip()
    try:
        send_stick(num)
    except ApiError:
        sender('Такого стикера не существует!')


def infa(to):
    sender(f'{to}, вероятность этого составляет {randint(1,100)}%')


def who(to):
    man = message.items[randint(2, len(message.items))-1]
    user_id = vk.users.get(user_ids=man['member_id'])[0]['id']
    info = message.text.replace('кто ', '')
    sender(f'{to}, {info} - {get_name(user_id)}')


def weather(to):
    city = message.text[7:]
    sender(f'{to}, {send_weather(city)}')


def what_it_is(to):
    name = message.text[10:]
    sender(f'{to}, {send_description(name)}')


husband_id = None
wife_id = None


def marry_command(to):
    if check_marriage(message.user_id) != '':
        sender(f'{to}, вы уже состоите в браке. Сначала разведитесь.')
        return
    name = message.text[5:]
    global wife_id
    global husband_id
    wife_id = get_id(name, message.event)
    husband_id = message.user_id
    wife = name_or_nick(wife_id)
    if wife_id == husband_id:
        sender(f'{to}, нельзя заключить брак с самим собой')
        return
    if check_marriage(wife_id) != '':
        sender(f'{to}, {wife} уже состоит в браке.')
        return

    def create_keyboard():
        keyboard = vk_api.keyboard.VkKeyboard(one_time=False)
        keyboard.add_button("Да", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
        keyboard.add_button("Нет", color=vk_api.keyboard.VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()
    sender(f'Согласен(на) ли {wife} стать мужем(женой) {to}?', keyboard=create_keyboard())

    def get_agreement(id1, id2):
        sender(f'{to}, время на согласие вышло. Повторите отправку команды позже.')
        return id1, id2
    global agreement
    agreement = Timer(30, get_agreement, [husband_id, wife_id, ])
    agreement.start()


def divorce_command(to):
    if check_marriage(message.user_id) == '':
        sender(f'{to}, вы не состоите в браке.')
        return
    husband = name_or_nick(check_marriage(message.user_id).split('_')[0])
    wife = name_or_nick(check_marriage(message.user_id).split('_')[1])
    divorce(message.user_id)
    if husband == to:
        sender(f'{to} расторг брак c {wife}')
    else:
        sender(f'{to} расторг брак c {husband}')


def commands_list():
    text = moji.emoji(':memo: Список команд:\n')
    commands_list_output = list()
    [commands_list_output.append(f'{k} - {v}\n') for k, v in commands.items()]
    commands_str = ''.join(commands_list_output)
    sender(text + commands_str)


def statuses_list():
    statuses_for_msg = statuses()
            
    def get_key(d, value):
        keys = list()
        [keys.append(k) if v == value else None for k, v in d.items()]
        return keys
            
    def get_names(user_ids):
        users_names_list = list()
        [users_names_list.append(name_or_nick(user_id)) for user_id in user_ids]
        user_names_str = '\n'.join(users_names_list)
        return user_names_str

    statuses_message = moji.emojize(":memo: Статусы пользователей беседы:\n")
    if len(get_names(get_key(statuses_for_msg, 5))) > 0:
        statuses_message += f"\n{temp_texts['STATUS5']} (5):\n{get_names(get_key(statuses_for_msg, 5))}\n"
    if len(get_names(get_key(statuses_for_msg, 4))) > 0:
        statuses_message += f"\n{temp_texts['STATUS4']} (4):\n{get_names(get_key(statuses_for_msg, 4))}\n"
    if len(get_names(get_key(statuses_for_msg, 3))) > 0:
        statuses_message += f"\n{temp_texts['STATUS3']} (3):\n{get_names(get_key(statuses_for_msg, 3))}\n"
    if len(get_names(get_key(statuses_for_msg, 2))) > 0:
        statuses_message += f"\n{temp_texts['STATUS2']} (2):\n{get_names(get_key(statuses_for_msg, 2))}\n"
    if len(get_names(get_key(statuses_for_msg, 1))) > 0:
        statuses_message += f"\n{temp_texts['STATUS1']} (1):\n{get_names(get_key(statuses_for_msg, 1))}"    
    sender(statuses_message)


def nicks_list():

    def get_names():
        users_names_list = list()
        i = 0
        for k, v in nicks().items():
            if (v is None or v.strip() == '') or v.split('|')[1] == ']':
                continue
            else:
                i += 1
                users_names_list.append(f"{i}. {name_or_nick(k)} - {get_name(k) + ' ' + get_surname(k)}")
        user_names_str = '\n'.join(users_names_list)
        return "Ников нету" if user_names_str.strip() == '' else user_names_str
    sender(moji.emojize(f":memo: Ники пользователей:\n\n{get_names()}"))


def marriages_list():
    marriages = list(check_marriages())

    def get_marriages():
        marriages_list_output = list()
        for i in range(0, len(marriages)):
            marriage = marriages[i]
            husband = marriage.split('_')[0]
            wife = marriage.split('_')[1]
            marriage_time = (dt.datetime.now() - dt.datetime.strptime(marriages[i].split('_')[2], '%d.%m.%Y')).days
            marriages_list_output.append(f"{i+1}. {name_or_nick(husband)} и {name_or_nick(wife)} ({marriage_time} дн.)")
        marriages_str = '\n'.join(marriages_list_output)
        return "Браков нету" if marriages_str.strip() == '' else marriages_str
    sender(moji.emojize(f":memo: Браки пользователей:\n\n{get_marriages()}"))


def preds_list():

    def get_preds():
        users_names_list = list()
        i = 0
        for k, v in preds().items():
            if v is None or v == 0:
                continue
            else:
                i += 1
                users_names_list.append(f"{i}. {name_or_nick(k)} ({v}/5)")
        user_names_str = '\n'.join(users_names_list)
        return "Предупреждений нету" if user_names_str.strip() == '' else user_names_str
    sender(moji.emojize(f":memo: Предупреждения пользователей:\n\n{get_preds()}"))


def ban_phrase(to):
    bad_word = message.text_low.replace('запрети фразу ', '')
    with open('Bad_words.txt', 'a') as file:
        file.write(f'\n{bad_word}')
    bad_words.add(bad_word)
    sender(f'{to}, данная фраза добавлена в список запрещенных.')


def unban_phrase(to):
    bad_word = message.text_low.replace('разреши фразу ', '')
    bad_words.remove(bad_word)
    with open('Bad_words.txt', 'w') as file:
        [file.write(f'{line}\n') for line in bad_words]
    sender(f'{to}, данная фраза убрана из списка запрещенных')


def bad_words_list():
    bad_words_str = ''
    bad_words_str += [f'{word.title()}, ' for word in bad_words]
    sender(f'Запрещенные фразы: {bad_words_str}')


def new_greeting(to):
    temp_texts['WELCOMING'] = message.text[18:].strip()
    render_new_temps()
    sender(f'{to}, новое приветствие установлено!')


def new_byeing(to):
    temp_texts['BYEBYING'] = message.text[15:].strip()
    render_new_temps()
    sender(f'{to}, новое прощание установлено!')


def new_kick_text(to):
    temp_texts['KICK_TEXT'] = message.text[17:].strip()
    render_new_temps()
    sender(f'{to}, новый текст кика установлен!')


def give_status(to):
    status = message.text[7:8].strip()
    if int(message.status) < int(status):
        sender(f'{to}, отказано в доступе ({check_status(message.user_id)}<={status})')
        return
    name = message.text[9:].strip()
    if get_name(get_id(name, message.event)) == "Участника с таким именем не существует":
        sender(f'{to}, участника с таким именем не существует!')
        return
    set_status(get_id(name, message.event), int(status))
    sender(f'{to}, {name} был установлен статус {status}!')


def kick(to):
    name = message.text[4:].strip()
    if check_status(get_id(name, message.event)):
        if check_status(get_id(name, message.event)) > message.status:
            sender(f'{to}, отказано в доступе '
                   f'({check_status(message.user_id)}<={check_status(get_id(name, message.event))})')
            return
    kick_user(get_id(name, message.event))


def pred(to):
    name = message.text[5:].strip()
    if check_status(get_id(name, message.event)):
        if check_status(get_id(name, message.event)) >= message.status:
            sender(f'{to}, отказано в доступе '
                   f'({check_status(message.user_id)}<={check_status(get_id(name, message.event))})')
            return
    if get_name(get_id(name, message.event)) == "Участника с таким именем не существует":
        sender(f'{to}, участника с таким именем не существует!')
        return
    add_pred_and_check(get_id(name, message.event))


def remove_pred(to):
    name = message.text[11:].strip()
    if check_status(get_id(name, message.event)):
        if check_status(get_id(name, message.event)) >= message.status:
            sender(f'{to}, отказано в доступе '
                   f'({check_status(message.user_id)}<={check_status(get_id(name, message.event))})')
            return
    if get_name(get_id(name, message.event)) == "Участника с таким именем не существует":
        sender(f'{to}, участника с таким именем не существует!')
        return
    sender(f"У {name_or_nick(get_id(name, message.event))} было снято 1 предупреждение.")
    remove_pred(get_id(name, message.event))


def reload_all(to):
    reg_all(message.event)
    reload_admins(message.event)
    sender(f'{to}, администраторы беседы обновились')


def set_nick(to):
    nick = message.text[8:].strip()
    set_nick(message.user_id, nick)
    sender(f'{to}, ник {nick} был установлен!')


def send_cat(to):
    sender(f'{to}, держи котика', photo=send_cats_urls())


agreement = None            


# Function have processing all requests
def chat_requests_processing():
    check_msg4bad_words()
    if agreement is not None:
        if agreement.is_alive():
            global wife_id
            global husband_id
            husband = name_or_nick(husband_id)
            wife = name_or_nick(wife_id)
            if message.text_low == f'[club{GROUP_ID}|@' \
                                   f'{vk_session.method("groups.getById", {"group_id": GROUP_ID})[0]["screen_name"]}]' \
                                   f' да' and message.user_id == wife_id:
                marry(husband_id, wife_id)
                sender(f'💍🤵👰 Поздравим {husband} и {wife} с заключением брака!')
                agreement.cancel()
                wife_id = None
                husband_id = None
            elif message.text_low == f'[club{GROUP_ID}|@' \
                                     f'{vk_session.method("groups.getById", {"group_id": GROUP_ID})[0]["screen_name"]}]' \ 
                                     f' нет' and message.user_id == wife_id:
                sender(f'{husband}, {wife} отверг(ла) ваше предложение.')
                agreement.cancel()
                wife_id = None
                husband_id = None
    if for_jorik():
        message.text_low = message.text_low[6:].strip()
        message.text = message.text[6:].strip()
        to = name_or_nick(message.user_id)
        
        if this_command('стикер '):
            new_thread(sticker, [message])
        elif this_command('инфа '):
            new_thread(infa, [to])
        elif this_command('кто '):
            new_thread(who, [message, to])
        elif this_command('погода '):
            new_thread(weather, [message, to])
        elif this_command('что такое '):
            new_thread(what_it_is, [message, to])
        elif this_command('брак '):
            new_thread(marry_command, [message, to])
        elif this_command('развод'):
            new_thread(divorce_command, [message, to])
        elif this_command('команды'):
            new_thread(commands_list)
        elif this_command('статусы'):
            new_thread(statuses_list)
        elif this_command('ники'):
            new_thread(nicks_list)
        elif this_command('браки'):
            new_thread(marriages_list)
        elif this_command('преды'):
            new_thread(preds_list)
        elif this_command('запрети фразу '): 
            new_thread(ban_phrase, [message])
        elif this_command('разреши фразу '):
            new_thread(unban_phrase, [message])
        elif this_command('запрещенные фразы'):
            new_thread(bad_words_list)
        elif this_command('новое приветствие:'):
            new_thread(new_greeting, [message, to])
        elif this_command('новое прощание:'):
            new_thread(new_byeing, [message, to])
        elif this_command('новый текст кика:'):
            new_thread(new_kick_text, [message, to])
        elif this_command('статус '):
            new_thread(give_status, [message, to])
        elif this_command('кик '):
            new_thread(kick, [message, to])
        elif this_command('пред '):
            new_thread(pred, [message, to])
        elif this_command('снять пред '):
            new_thread(remove_pred, [message, to])
        elif this_command('обновить'):
            new_thread(reload_all, [message, to])
        elif this_command('мне ник '):
            new_thread(set_nick, [message, to])
        elif this_command('котик'):
            new_thread(send_cat, [to])
    

def group_requests_processing(event):
    if event.type == VkBotEventType.WALL_POST_NEW and mailing:
        id_ = event.object['id']
        owner_id_ = event.group_id
        wall_id = f'wall-{owner_id_}_{id_}'
        sender('Новый пост в группе!', wall_post=wall_id)

        
# MAIN PART OF THE CODE

# Connecting to Vk
vk_session = vk_api.VkApi(token=main_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

vk_session1 = vk_api.VkApi(token=main_token)
longpoll_group = VkBotLongPoll(vk_session1, GROUP_ID)
upload = VkUpload(vk)

# Rendering bad words
bad_words = set()
render_bad_words()
render_temps()

message = Message(None, None, None, None, None, None, None)


def listen_group():
    for event in longpoll_group.listen():
        group_requests_processing(event)
    
        
def listen_chat():
    global message
    global longpoll_group
    try:
        for event in longpoll.listen():
            try:
                if event.from_chat:
                    if event.type == VkEventType.MESSAGE_NEW:
                        message = Message(event, get_name(event.user_id), get_surname(event.user_id),
                                          check_nick(event.user_id), event.text, check_status(event.user_id),
                                          vk_session.method('messages.getConversationMembers',
                                                            {'peer_id': event.peer_id})['items'])
                        register(event.user_id)                        
                        if CHAT_ID is '':
                            global CHAT_ID
                            CHAT_ID = message.chat_id
                            group = Thread(target=listen_group)
                            group.start()
                        if event.text != '':
                            chat_requests_processing()
                    if event.type_id == VkChatEventType.USER_JOINED:
                        sender(f'{temp_texts["WELCOMING"]}')
                        reg_all(message.event)
                    elif event.type_id == VkChatEventType.USER_LEFT:
                        remove_from_db(message.event.user_id)
                        sender(f'{temp_texts["BYEBYING"]}')
                    elif event.type_id == VkChatEventType.USER_KICKED:
                        remove_from_db(message.event.user_id)
                        sender(f'{temp_texts["KICK_TEXT"]}')
            except ApiError as err:
                if str(err).startswith('[113]'):
                    continue
    except ConnectionError:
        sender('Проблемы с соединением на сервере!')


if __name__ == "__main__":
    chat = Thread(target=listen_chat)
    chat.start()
    chat.join()
