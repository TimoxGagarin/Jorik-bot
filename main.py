import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.upload import VkUpload
from vk_api.exceptions import ApiError
from random import randint
from config import main_token, commands, temp_texts
from UseDatabase import register, check_status, set_status, statuses, remove_from_db, check_nick, nicks, set_nick, check_preds, preds, add_pred, remove_pred
from parsers import send_weather, send_description, send_valute, send_cat
import datetime as dt
import emoji


#Function have writting text to logs file
def write_logs(text):
    try:
        with open('logs.log', 'a') as file:
            file.write(f'{text}\n')
    except UnicodeEncodeError:
        pass

            
#Function have getting all info from message to dictionary and to logs
def msg_info_write(event):
    chat_id = event.chat_id
    user_id = event.user_id
    name = ''
    nick = check_nick(user_id)
    name = get_name(True,user_id)
    time = dt.datetime.now().strftime("%d.%m.%Y] (%H:%M")
    status = check_status(user_id)
    if status == None:
        status = 0
        status_text = 'User'
    if status != 0:
        status_text = temp_texts['STATUS' + str(status)]
    else:
        status_text = 'User'
    msg_info = {
        'chat_id': chat_id,
        'name': name,
        'nick': nick,
        'user_id': user_id,
        'status_text': status_text,
        'status': status,
        'items': vk_session.method('messages.getConversationMembers', {'peer_id':event.peer_id})['items'],
        'time': time,
        'text': event.text.lower(),
        'orig_text': event.text,
        'event': event,
    }
    log_line = f'[{time}) [{status_text}] {name} отправил сообщение: "{event.text}"'
    write_logs(log_line)
    return msg_info        
        
def get_name(only_name, user_id):
    if only_name == False:
        return f"[id{user_id}|{vk.users.get(user_ids = user_id)[0]['first_name'] + ' ' + vk.users.get(user_ids = user_id)[0]['last_name']}]"
    elif only_name == True:
        return f"[id{user_id}|{vk.users.get(user_ids = user_id)[0]['first_name']}]"


def name_or_nick(user_id):
    to = get_name(True, user_id)
    if check_nick(user_id):
        if check_nick(user_id).split('|')[1] != ']':
            to = check_nick(user_id)
    return to
                        
#Function have rendering bad words from the file
def render_bad_words():
    with open('Bad_words.txt', 'r') as file:
        for line in file:
            bad_words.add(line.replace('\n', ''))


#Function have rendering temps from the file
def render_temps():
    with open('temp_texts.txt', 'r') as file:
        for line in file:
            try:
                temp = line.split(':')[0]
                temp_texts[temp] = line[len(temp) + 1:]
            except Exception as err:
                time = dt.datetime.now().strftime("%d.%m.%Y] (%H:%M")
                write_logs(f'[{time}) Ошибка: {str(err)}')


#Function have rendering temp to temps file
def render_new_temps():
    with open('temp_texts.txt', 'w') as file:
        for k, v in temp_texts.items():
            file.write(f'{k}: {v}\n')

                
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


def get_id(name, event) -> bool:
    people_profiles = vk_session.method('messages.getConversationMembers', {'peer_id' :event.peer_id})['profiles']
    for member in people_profiles:
        if (member['last_name'] == name) or (member['first_name'] == name) or (member['first_name'] + ' ' + member['last_name'] == name):
            return member['id']
        elif str(member['id']) == str(name.split('|')[0].replace('[id', '')):
            return member['id']


#Function send text message
def sender(text):
    vk_session.method('messages.send', {'chat_id':msg_info_dict['chat_id'], 'message' : text, 'random_id' : 0})


#Function send sticker from getting number
def send_stick(number):
    vk_session.method('messages.send', {'chat_id':msg_info_dict['chat_id'], 'sticker_id' : number, 'random_id' : 0})    


#Functions send photo
def upload_photo(photo):
    response = upload.photo_messages(photo)[0]
    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']
    return owner_id, photo_id, access_key


def send_photo(owner_id, photo_id, access_key):
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk_session.method('messages.send', {'random_id': 0, 'chat_id':msg_info_dict['chat_id'], 'attachment':attachment})


#Function kick user from the chat
def kick_user(user_id):
    to = name_or_nick(user_id)
    remove_from_db(user_id)
    vk_session.method('messages.removeChatUser', {'chat_id':msg_info_dict['chat_id'], 'user_id': user_id, 'random_id':0})
    sender(f"{to} был кикнут за нарушение правил беседы")


def add_pred_and_check(user_id):
    add_pred(user_id)
    to = name_or_nick(user_id)
    sender(f'{to} получает предупреждение ({check_preds(user_id)}/{temp_texts["PREDS"]})')
    if check_preds(user_id) == temp_texts['PREDS']:
        kick_user(user_id)
    
#Function have checking target of message
def for_jorik() -> bool:
    return msg_info_dict['text'].startswith('жорик,')


def compare_statuses(comm):
    if commands[comm] > msg_info_dict['status']:
        sender(f'{msg_info_dict["name"]}, отказано в доступе ({msg_info_dict["status"]}<{commands[comm]})')
        return False
    return True


#Function have processing all requests
def request_processing():
    check_msg4bad_words()
    if for_jorik():
        #Users part
        msg_info_dict['text'] = msg_info_dict['text'][6:].strip()
        msg_info_dict['orig_text'] = msg_info_dict['orig_text'][6:].strip()
        to = name_or_nick(msg_info_dict['user_id'])
        if msg_info_dict['text'].startswith('стикер ') and compare_statuses('стикер '):
            num = msg_info_dict['text'].replace('стикер ', '').strip()
            try:
                send_stick(num)
            except ApiError:
                sender('Такого стикера не существует!')
        elif msg_info_dict['text'].startswith('инфа ') and compare_statuses('инфа '):
            sender(f'{to}, вероятность этого составляет {randint(1,100)}%')
        elif msg_info_dict['text'].startswith('кто ') and compare_statuses('кто '):
            man = msg_info_dict['items'][randint(2, len(msg_info_dict['items']))-1]
            user_id = vk.users.get(user_ids=man['member_id'])[0]['id']
            info = msg_info_dict['text'].replace('кто ', '')
            sender(f'{to}, {info} - {get_name(False, user_id)}')
        elif msg_info_dict['text'].startswith('погода ') and compare_statuses('погода '):
            city = msg_info_dict['orig_text'][9:]
            sender(f'{to}, {send_weather(city)}')
        elif msg_info_dict['text'].startswith('что такое ') and compare_statuses('что такое '):
            name = msg_info_dict['orig_text'][10:]
            sender(f'{to}, {send_description(name)}')
        elif msg_info_dict['text'].startswith('курс ') and compare_statuses('курс '):
            code = msg_info_dict['text'][5:]
            sender(f'{to}, {send_valute(code)}')
        elif msg_info_dict['text'].startswith('команды') and compare_statuses('команды '):
            text = f'{to}, список команд:\n'
            for k,v in commands.items():
                text += f'{k} - {v}\n'
            sender(text)
        elif msg_info_dict['text'].startswith('статусы') and compare_statuses('статусы '):
            statuses_for_msg = statuses()
            def get_key(d, value):
                keys = list()
                for k, v in d.items():
                    if v == value:
                        keys.append(k)
                return keys
            
            def get_names(user_ids):
                users_names_list = list()
                for user_id in user_ids:
                    users_names_list.append(name_or_nick(user_id))
                user_names_str = '\n'.join(users_names_list)
                if user_names_str.strip() == '':
                    return "Никого"
                return user_names_str
            
            sender(f"Статусы пользователей беседы:\n\n{temp_texts['STATUS5']}:\n\n{get_names(get_key(statuses_for_msg, 5))}\n\n{temp_texts['STATUS4']}:\n\n{get_names(get_key(statuses_for_msg, 4))}\n\n{temp_texts['STATUS3']}:\n\n{get_names(get_key(statuses_for_msg, 3))}\n\n{temp_texts['STATUS2']}:\n\n{get_names(get_key(statuses_for_msg, 2))}\n\n{temp_texts['STATUS1']}:\n\n{get_names(get_key(statuses_for_msg, 1))}")
        elif msg_info_dict['text'].startswith('ники') and compare_statuses('ники '):
            users_names_list = []
            def get_names():
                users_names_list = list()
                for k,v in nicks().items():
                    if v == None or v.strip() == '':
                        continue
                    if  v.split('|')[1] == ']':
                        continue
                    users_names_list.append(f"{v} - {name_or_nick(k)}")
                user_names_str = '\n'.join(users_names_list)
                if user_names_str.strip() == '':
                    return "Ников нету"
                return user_names_str
                
            sender(f"Ники пользователей:\n\n{get_names()}")
        elif msg_info_dict['text'].startswith('преды') and compare_statuses('преды '):
            users_names_list = []
            def get_preds():
                users_names_list = list()
                for k,v in preds().items():
                    if v == None or v == 0:
                        continue
                    if  v == 0:
                        continue
                    users_names_list.append(f"{name_or_nick(k)} - {v}")
                user_names_str = '\n'.join(users_names_list)
                if user_names_str.strip() == '':
                    return "Предупреждений нету"
                return user_names_str
                
            sender(f"Предупреждения пользователей:\n\n{get_preds()}")
        elif msg_info_dict['text'].startswith('запрети фразу ') and compare_statuses('запрети фразу ') : 
            bad_word = msg_info_dict['text'].replace('запрети фразу ', '')
            with open('Bad_words.txt', 'a') as file:
                file.write(f'\n{bad_word}')
            bad_words.add(bad_word)
            sender('Данная фраза добавлена в список запрещенных.')
        elif msg_info_dict['text'].startswith('разреши фразу ') and compare_statuses('разреши фразу '):
            bad_word = msg_info_dict['text'].replace('разреши фразу ', '')
            bad_words.remove(bad_word)
            with open('Bad_words.txt', 'w') as file:
                for line in bad_words:
                    file.write(f'{line}\n')
            sender('Данная фраза убрана из списка запрещенных')
        elif msg_info_dict['text'].startswith('запрещенные фразы'):
            bad_words_str = ''
            for word in bad_words:
                bad_words_str += f'{word.title()}, '
            sender(f'Запрещенные фразы: {bad_words_str}')
        elif msg_info_dict['text'].startswith('новое приветствие:') and compare_statuses('новое приветствие:') :
            temp_texts['WELCOMING'] = msg_info_dict['orig_text'][18:].strip()
            render_new_temps()
            sender(f'{msg_info_dict["name"]}, новое приветствие установлено!')
        elif msg_info_dict['text'].startswith('новое прощание:') and compare_statuses('новое прощание:'):
            temp_texts['BYEBYING'] = msg_info_dict['orig_text'][15:].strip()
            render_new_temps()
            sender(f'{to}, новое прощание установлено!')
        elif msg_info_dict['text'].startswith('новый текст кика:') and compare_statuses('новый текст кика: '):
            temp_texts['KICK_TEXT'] = msg_info_dict['orig_text'][17:].strip()
            render_new_temps()
            sender(f'{to}, новый текст кика установлен!')
        elif msg_info_dict['text'].startswith('статус ') and compare_statuses('статус '):
            status = msg_info_dict['orig_text'][7:8].strip()
            if msg_info_dict['status'] < int(status):
                sender(f'{to}, отказано в доступе ({check_status(msg_info_dict["user_id"])}<={status})')
                return
            name = msg_info_dict['orig_text'][9:].strip()
            set_status(get_id(name, msg_info_dict["event"]), int(status))
            sender(f'{to}, {get_name(True, get_id(name, msg_info_dict["event"]))} был установлен статус {status}!')
        elif msg_info_dict['text'].startswith('кик ') and compare_statuses('кик '):
            name = msg_info_dict['orig_text'][4:].strip()
            if check_status(get_id(name, msg_info_dict['event'])):
                if check_status(get_id(name, msg_info_dict['event'])) > msg_info_dict['status']:
                    sender(f'{to}, отказано в доступе ({check_status(msg_info_dict["user_id"])}<={check_status(get_id(name, msg_info_dict["event"]))})')
                    return
            kick_user(get_id(name, msg_info_dict["event"]))
        elif msg_info_dict['text'].startswith('пред ') and compare_statuses('пред '):
            name = msg_info_dict['orig_text'][5:].strip()
            if check_status(get_id(name, msg_info_dict['event'])):
                if check_status(get_id(name, msg_info_dict['event'])) > msg_info_dict['status']:
                    sender(f'{to}, отказано в доступе ({check_status(msg_info_dict["user_id"])}<={check_status(get_id(name, msg_info_dict["event"]))})')
                    return
            add_pred_and_check(get_id(name, msg_info_dict["event"]))
        elif msg_info_dict['text'].startswith('снять пред ') and compare_statuses('снять пред '):
            name = msg_info_dict['orig_text'][11:].strip()
            if check_status(get_id(name, msg_info_dict['event'])):
                if check_status(get_id(name, msg_info_dict['event'])) > msg_info_dict['status']:
                    sender(f'{to}, отказано в доступе ({check_status(msg_info_dict["user_id"])}<={check_status(get_id(name, msg_info_dict["event"]))})')
                    return
            sender(f"У {name_or_nick(get_id(name, msg_info_dict['event']))} было снято 1 предупреждение.")
            remove_pred(get_id(name, msg_info_dict["event"]))
        elif msg_info_dict['text'].startswith('обновить') and compare_statuses('обновить '):
            reload_admins(msg_info_dict["event"])
            sender(f'{to}, администраторы беседы обновились')
        elif msg_info_dict['text'].startswith('мне ник ') and compare_statuses('мне ник '):
            nick = msg_info_dict['orig_text'][8:].strip()
            set_nick(msg_info_dict['user_id'], nick)
            sender(f'{to}, ник {nick} был установлен!')
        
        #Отладочные команды
        elif msg_info_dict['text'].startswith('айди') and compare_statuses('айди '):
            name = msg_info_dict['orig_text'][4:].strip()
            sender(f'{get_id(name, msg_info_dict["event"])}')


#Function kick user if he wrote bad word from the list:       
def check_msg4bad_words():
    if msg_info_dict['status'] < 4:
        for word in msg_info_dict['text'].split(' '):
            if word in bad_words:
                print('.-.')
                add_pred_and_check(msg_info_dict['user_id'])
    

#MAIN PART OF THE CODE

#Connecting to Vk
vk_session = vk_api.VkApi(token = main_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
upload = VkUpload(vk)

#Renderring bad words
bad_words = set()
render_bad_words()
render_temps()

#Message info template
msg_info_dict = {
            'chat_id': None,
            'name': None,
            'user_id': None,
            'status': None,
            'items': None,
            'time': None,
            'text': None,
            'event': None,
        }

try:
    for event in longpoll.listen():
        try:
            if event.from_chat:
                if event.type == VkEventType.MESSAGE_NEW:
                    msg_info_dict = msg_info_write(event)
                    register(event.user_id)
                    if event.text: 
                        request_processing()
                if event.type_id == VkChatEventType.USER_JOINED:
                    sender(f'{temp_texts["WELCOMING"]}')
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
#except ReadTimeout:
    #sender('Проблемы с соединением на сервере!')
#except Exception as err:
    #time = dt.datetime.now().strftime("%d.%m.%Y] (%H:%M")
    #print(f'[{time}) Ошибка: {str(err)}')
    #write_logs(f'[{time}) Ошибка: {str(err)}')
