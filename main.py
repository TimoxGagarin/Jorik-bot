import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
from vk_api.exceptions import ApiError
from random import randint
from config import main_token, commands, temp_texts
from Message import Message
from UseDatabase import register, check_status, set_status, statuses, remove_from_db, check_nick, nicks, set_nick, check_preds, preds, add_pred, remove_pred
from parsers import send_weather, send_description, send_cat
import datetime as dt
from threading import Thread
import emoji as moji


def get_name(user_id):
        try:
                return  f"[id{user_id}|{vk.users.get(user_ids = user_id)[0]['first_name']}]"
        except IndexError:
                return "Участника с таким именем не существует"


def get_surname(user_id):
        try:
                return  f"[id{user_id}|{vk.users.get(user_ids = user_id)[0]['last_name']}]"
        except IndexError:
                return "Участника с таким именем не существует"
        
def name_or_nick(user_id):
        to = get_name(user_id)
        if check_nick(user_id):
            if check_nick(user_id).split('|')[1] != ']':
                to = check_nick(user_id)
        return to

    
#Function have rendering bad words from the file
def render_bad_words():
    with open('Bad_words.txt', 'r') as file:
        [bad_words.add(line.replace('\n', '')) for line in file]


#Function have rendering temps from the file
def render_temps():
    with open('temp_texts.txt', 'r') as file:
        for line in file:
            try:
                temp = line.split(':')[0]
                temp_texts[temp] = moji.emojize(line[len(temp) + 1:])
            except Exception as err:
                time = dt.datetime.now().strftime("%d.%m.%Y] (%H:%M")


#Function have rendering temp to temps file
def render_new_temps():
    with open('temp_texts.txt', 'w') as file:
        try:
                [file.write(str(f'{k}: {moji.demojize(v)}\n')) for k, v in temp_texts.items()]
        except TypeError:
                pass

                
#Function check admin permissions          
def reload_admins(event):
        people_items = vk_session.method('messages.getConversationMembers', {'peer_id' :event.peer_id})['items']
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


def reg_all():
    members = vk_session.method('messages.getConversationMembers', {'peer_id' :event.peer_id})['profiles']
    [register(member['id']) for member in members]


def get_id(name, event) -> bool:
    people_profiles = vk_session.method('messages.getConversationMembers', {'peer_id' :event.peer_id})['profiles']
    for member in people_profiles:
            if ((member['last_name'] == name) or (member['first_name'] == name) or  (member['first_name'] + ' ' + member['last_name'] == name)) or str(member['id']) == str(name.split('|')[0].replace('[id', '')):
                    return member['id']


#Function send text message
def sender(text):
    vk_session.method('messages.send', {'chat_id':message.chat_id, 'message' : text, 'random_id' : 0})


#Function send sticker from getting number
def send_stick(number):
    vk_session.method('messages.send', {'chat_id':message.chat_id, 'sticker_id' : number, 'random_id' : 0})    


#Functions send photo
def upload_photo(photo):
    response = upload.photo_messages(photo)[0]
    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']
    return owner_id, photo_id, access_key


def send_photo(owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk_session.method('messages.send', {'random_id': 0, 'chat_id':message.chat_id, 'attachment':attachment})


#Function kick user from the chat
def kick_user(user_id):
    to = name_or_nick(user_id)
    remove_from_db(user_id)
    vk_session.method('messages.removeChatUser', {'chat_id':message.chat_id, 'user_id': user_id, 'random_id':0})
    sender(f"{to} был кикнут за нарушение правил беседы")


def add_pred_and_check(user_id):
    add_pred(user_id)
    to = name_or_nick(user_id)
    sender(f'{to} получает предупреждение ({check_preds(user_id)}/{temp_texts["PREDS"]})')
    if check_preds(user_id) == temp_texts['PREDS']:
        kick_user(user_id)
    
#Function have checking target of message
def for_jorik() -> bool:
    return message.text_low.startswith('жорик,')


def compare_statuses(comm):
    if commands[comm] > message.status:
        sender(f'{message.name}, отказано в доступе ({message.status}<{commands[comm]})')
        return False
    return True


#Function have processing all requests
def request_processing():
    check_msg4bad_words()
    if for_jorik():
        #Users part
        message.text_low = message.text_low[6:].strip()
        message.text = message.text[6:].strip()
        to = name_or_nick(message.user_id)
        if message.text_low.startswith('стикер ') and compare_statuses('стикер '):
            num = message.text_low.replace('стикер ', '').strip()
            try:
                send_stick(num)
            except ApiError:
                sender('Такого стикера не существует!')
        elif message.text_low.startswith('инфа ') and compare_statuses('инфа '):
            sender(f'{to}, вероятность этого составляет {randint(1,100)}%')
        elif message.text_low.startswith('кто ') and compare_statuses('кто '):
            man = message.items[randint(2, len(message.items))-1]
            user_id = vk.users.get(user_ids=man['member_id'])[0]['id']
            info = message.text.replace('кто ', '')
            sender(f'{to}, {info} - {get_name(user_id)}')
        elif message.text_low.startswith('погода ') and compare_statuses('погода '):
            city = message.text[9:]
            sender(f'{to}, {send_weather(city)}')
        elif message.text_low.startswith('что такое ') and compare_statuses('что такое '):
            name = message.text[10:]
            sender(f'{to}, {send_description(name)}')
        elif message.text_low.startswith('курс ') and compare_statuses('курс '):
            code = message.text_low[5:]
            sender(f'{to}, {send_valute(code)}')
        elif message.text_low.startswith('команды') and compare_statuses('команды '):
            text = f'{to}, список команд:\n'
            commands_list = list()
            [commands_list.append(f'{k} - {v}\n') for k,v in commands.items()]
            commands_str = '\n'.join(commands_list)
            sender(text + commands_str)
        elif message.text_low.startswith('статусы') and compare_statuses('статусы '):
            statuses_for_msg = statuses()
            def get_key(d, value):
                keys = list()
                [keys.append(k) if v == value else None for k, v in d.items()]
                return keys
            
            def get_names(user_ids):
                users_names_list = list()
                [users_names_list.append(name_or_nick(user_id)) for user_id in user_ids]
                user_names_str = '\n'.join(users_names_list)
                return "Никого" if user_names_str.strip() == '' else user_names_str
            sender(f"Статусы пользователей беседы:\n\n{temp_texts['STATUS5']}\n\n{get_names(get_key(statuses_for_msg, 5))}\n\n{temp_texts['STATUS4']}\n\n{get_names(get_key(statuses_for_msg, 4))}\n\n{temp_texts['STATUS3']}\n\n{get_names(get_key(statuses_for_msg, 3))}\n\n{temp_texts['STATUS2']}\n\n{get_names(get_key(statuses_for_msg, 2))}\n\n{temp_texts['STATUS1']}\n\n{get_names(get_key(statuses_for_msg, 1))}")
        elif message.text_low.startswith('ники') and compare_statuses('ники '):
            users_names_list = []
            def get_names():
                users_names_list = list()
                for k,v in nicks().items():
                        if (v == None or v.strip() == '') or v.split('|')[1] == ']':
                                continue
                        else:
                                users_names_list.append(f"{name_or_nick(k)} - {get_name(k) + ' '+get_surname(k)}")
                user_names_str = '\n'.join(users_names_list)
                return "Ников нету" if user_names_str.strip() == '' else user_names_str
            sender(f"Ники пользователей:\n\n{get_names()}")
        elif message.text_low.startswith('преды') and compare_statuses('преды '):
            users_names_list = []
            def get_preds():
                users_names_list = list()
                for k,v in preds().items():
                        if v == None or v == 0:
                                continue
                        else:
                                users_names_list.append(f"{name_or_nick(k)} - {v}")
                user_names_str = '\n'.join(users_names_list)
                return "Предупреждений нету" if user_names_str.strip() == '' else user_names_str
            sender(f"Предупреждения пользователей:\n\n{get_preds()}")
        elif message.text_low.startswith('запрети фразу ') and compare_statuses('запрети фразу ') : 
            bad_word = message.text_low.replace('запрети фразу ', '')
            with open('Bad_words.txt', 'a') as file:
                file.write(f'\n{bad_word}')
            bad_words.add(bad_word)
            sender('Данная фраза добавлена в список запрещенных.')
        elif message.text_low.startswith('разреши фразу ') and compare_statuses('разреши фразу '):
            bad_word = message.text_low.replace('разреши фразу ', '')
            bad_words.remove(bad_word)
            with open('Bad_words.txt', 'w') as file:
                [file.write(f'{line}\n') for line in bad_words]
            sender('Данная фраза убрана из списка запрещенных')
        elif message.text_low.startswith('запрещенные фразы'):
            bad_words_str = ''
            bad_words_str += [f'{word.title()}, ' for word in bad_words]
            sender(f'Запрещенные фразы: {bad_words_str}')
        elif message.text_low.startswith('новое приветствие:') and compare_statuses('новое приветствие:') :
            temp_texts['WELCOMING'] = message.text[18:].strip()
            render_new_temps()
            sender(f'{to}, новое приветствие установлено!')
        elif message.text_low.startswith('новое прощание:') and compare_statuses('новое прощание:'):
            temp_texts['BYEBYING'] = message.text[15:].strip()
            render_new_temps()
            sender(f'{to}, новое прощание установлено!')
        elif message.text_low.startswith('новый текст кика:') and compare_statuses('новый текст кика:'):
            temp_texts['KICK_TEXT'] = message.text[17:].strip()
            render_new_temps()
            sender(f'{to}, новый текст кика установлен!')
        elif message.text_low.startswith('статус ') and compare_statuses('статус '):
            status = message.text[7:8].strip()
            if message.status < int(status):
                sender(f'{to}, отказано в доступе ({check_status(message.user_id)}<={status})')
                return
            name = message.text[9:].strip()
            if get_name(get_id(name, message.event)) == "Участника с таким именем не существует":
                sender(f'{to}, участника с таким именем не существует!')
                return
            set_status(get_id(name, message.event), int(status))
            sender(f'{to}, {name} был установлен статус {status}!')
        elif message.text_low.startswith('кик ') and compare_statuses('кик '):
            name = msg_info_dict['orig_text'][4:].strip()
            if check_status(get_id(name, message.event)):
                if check_status(get_id(name, message.event)) > message.status:
                    sender(f'{to}, отказано в доступе ({check_status(message.user_id)}<={check_status(get_id(name, message.event))})')
                    return
            kick_user(get_id(name, message.event))
        elif message.text_low.startswith('пред ') and compare_statuses('пред '):
            name = message.text[5:].strip()
            if check_status(get_id(name, message.event)):
                if check_status(get_id(name, message.event)) >= message.status:
                    sender(f'{to}, отказано в доступе ({check_status(message.user_id)}<={check_status(get_id(name, message.event))})')
                    return
            if get_name(True, get_id(name, message.event)) == "Участника с таким именем не существует":
                sender(f'{to}, участника с таким именем не существует!')
                return
            add_pred_and_check(get_id(name, msg_info_dict["event"]))
        elif message.text_low.startswith('снять пред ') and compare_statuses('снять пред '):
            name = message.text[11:].strip()
            if check_status(get_id(name, message.event)):
                if check_status(get_id(name, message.event)) >= message.status:
                    sender(f'{to}, отказано в доступе ({check_status(message.user_id)}<={check_status(get_id(name, message.event))})')
                    return
            if get_name(get_id(name, message.event)) == "Участника с таким именем не существует":
                sender(f'{to}, участника с таким именем не существует!')
                return
            sender(f"У {name_or_nick(get_id(name, message.event))} было снято 1 предупреждение.")
            remove_pred(get_id(name, message.event))
        elif message.text_low.startswith('обновить') and compare_statuses('обновить '):
            reg_all()
            reload_admins(message.event)
            sender(f'{to}, администраторы беседы обновились')
        elif message.text_low.startswith('мне ник ') and compare_statuses('мне ник '):
            nick = message.text[8:].strip()
            set_nick(message.user_id, nick)
            sender(f'{to}, ник {nick} был установлен!')
        
        #Отладочные команды
        elif message.text_low.startswith('айди') and compare_statuses('айди '):
            name = message.text[4:].strip()
            sender(f'{get_id(name, message.event)}')


#Function kick user if he wrote bad word from the list:       
def check_msg4bad_words():
    if message.status < 4:
        [add_pred_and_check(message.user_id) if word in bad_words else None for word in message.text_low.split(' ')]
    

#MAIN PART OF THE CODE

#Connecting to Vk
vk_session = vk_api.VkApi(token = main_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

vk_session1 = vk_api.VkApi(token = main_token)
longpoll_group = VkBotLongPoll(vk_session1, 205699866)
upload = VkUpload(vk)

#Renderring bad words
bad_words = set()
render_bad_words()
render_temps()

message = None

def listen_chat():
        global message
        try:
            for event in longpoll.listen():
                try:
                    if event.from_chat:
                        if event.type == VkEventType.MESSAGE_NEW:
                            message = Message(event, get_name(event.user_id), get_surname(event.user_id), check_nick(event.user_id), event.text, dt.datetime.now().strftime("%d.%m.%Y] (%H:%M"),check_status(event.user_id), vk_session.method('messages.getConversationMembers', {'peer_id':event.peer_id})['items'])
                            register(event.user_id)
                            if event.text != '':
                                    request_processing()
                        if event.type_id == VkChatEventType.USER_JOINED:
                            sender(f'{temp_texts["WELCOMING"]}')
                            reg_all()
                        elif event.type_id == VkChatEventType.USER_LEFT:
                            remove_from_db(event.user_id)
                            sender(f'{temp_texts["BYEBYING"]}')
                        elif event.type_id == VkChatEventType.USER_KICKED:
                            sender(f'{temp_texts["KICK_TEXT"]}')
                except ApiError as err:
                    if str(err).startswith('[113]'):
                        continue
        except ConnectionError:
            sender('Проблемы с соединением на сервере!')



def listen_group():
        for event in longpoll_group.listen():
                print('Салями попалами')   

chat = Thread(target=listen_chat())
group = Thread(target=listen_group())

chat.start(),group.start()
chat.join(),group.join()
