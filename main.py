import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.upload import VkUpload
from vk_api.exceptions import ApiError
from random import randint
from config import main_token
from parsers import send_weather, send_description, send_valute, send_cat
import datetime as dt


#Function have writting text to logs file
def write_logs(text):
    with open('logs.log', 'a') as file:
        file.write(f'{text}\n')

            
#Function have getting all info from message to dictionary and to logs
def msg_info_write(event):
    chat_id = event.chat_id
    user_id = event.user_id
    name = vk.users.get(user_ids = user_id)[0]['first_name']
    time = dt.datetime.now().strftime("%d.%m.%Y] (%H:%M")
    status = ''
    if check_admin(user_id, event):
        status = 'Admin'
    else:
        status = 'User'
    msg_info = {
        'chat_id': chat_id,
        'name': name,
        'user_id': user_id,
        'status': status,
        'items': vk_session.method('messages.getConversationMembers', {'peer_id':event.peer_id})['items'],
        'time': time,
        'text': event.text.lower(),
        'orig_text': event.text,
    }
    log_line = f'[{time}) [{status}] {name} отправил сообщение: "{event.text}"'
    write_logs(log_line)
    return msg_info        
        
    
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
def check_admin(user_id, event) -> bool:
    try:
        people_items = vk_session.method('messages.getConversationMembers', {'peer_id' :event.peer_id})['items']
        for member in people_items:
            if member['member_id'] == user_id:
                if member['is_admin']:
                    return True
    except KeyError:
        return False
    return False


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
def kick_user():
    vk_session.method('messages.removeChatUser', {'chat_id':msg_info_dict['chat_id'], 'user_id':msg_info_dict['user_id'], 'random_id':0})

    
#Function have checking target of message
def for_jorik() -> bool:
    return msg_info_dict['text'].startswith('жорик,')


#Function have processing all requests
def request_processing():
    check_msg4bad_words()
    if for_jorik():
        #Users part
        if msg_info_dict['status'] == 'Admin' or msg_info_dict['status'] != 'Admin':
            msg_info_dict['text'] = msg_info_dict['text'][6:].strip()
            msg_info_dict['orig_text'] = msg_info_dict['orig_text'][6:].strip()
            if msg_info_dict['text'].startswith('стикер '):
                num = msg_info_dict['text'].replace('стикер ', '').strip()
                try:
                    send_stick(num)
                except ApiError:
                    sender('Такого стикера не существует!')
            elif msg_info_dict['text'].startswith('инфа '):
                sender(f'{msg_info_dict["name"]}, вероятность этого составляет {randint(1,100)}%')
            elif msg_info_dict['text'].startswith('кто '):
                man = msg_info_dict['items'][randint(2, len(msg_info_dict['items']))-1]
                user = f"{vk.users.get(user_ids=man['member_id'])[0]['first_name']} {vk.users.get(user_ids=man['member_id'])[0]['last_name']}"
                info = msg_info_dict['text'].replace('кто ', '')
                sender(f'{msg_info_dict["name"]}, {info} - {user}')
            elif msg_info_dict['text'].startswith('погода в '):
                city = msg_info_dict['orig_text'][9:]
                sender(f'{msg_info_dict["name"]}, {send_weather(city)}')
            elif msg_info_dict['text'].startswith('что такое '):
                name = msg_info_dict['orig_text'][10:]
                sender(f'{msg_info_dict["name"]}, {send_description(name)}')
            elif msg_info_dict['text'].startswith('курс '):
                code = msg_info_dict['text'][5:]
                sender(f'{msg_info_dict["name"]}, {send_valute(code)}')
        #Admins part
        if msg_info_dict['status'] == 'Admin':
            if msg_info_dict['text'].startswith('запрети фразу '): 
                bad_word = msg_info_dict['text'].replace('запрети фразу ', '')
                with open('Bad_words.txt', 'a') as file:
                    file.write(f'\n{bad_word}')
                bad_words.add(bad_word)
                sender('Данная фраза добавлена в список запрещенных.')
            elif msg_info_dict['text'].startswith('разреши фразу '):
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
            elif msg_info_dict['text'].startswith('новое приветствие:'): #Тексты не сохраняются, как надо
                temp_texts['WELCOMING'] = msg_info_dict['orig_text'][18:].strip()
                render_new_temps()
                sender(f'{msg_info_dict["name"]}, новое приветствие установлено!')
            elif msg_info_dict['text'].startswith('новое прощание:'):
                temp_texts['BYEBYING'] = msg_info_dict['orig_text'][15:].strip()
                render_new_temps()
                sender(f'{msg_info_dict["name"]}, новое прощание установлено!')
            elif msg_info_dict['text'].startswith('новый текст кика:'):
                temp_texts['KICK_TEXT'] = msg_info_dict['orig_text'][17:].strip()
                render_new_temps()
                sender(f'{msg_info_dict["name"]}, новый текст кика установлен!')


#Function kick user if he wrote bad word from the list:       
def check_msg4bad_words():
    if msg_info_dict['status'] != 'Admin':
        for word in msg_info_dict['text'].split(' '):
            if word in bad_words:
                kick_user()


#MAIN PART OF THE CODE

vk_session = vk_api.VkApi(token = main_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
upload = VkUpload(vk)
            
bad_words = set()
render_bad_words()

temp_texts = {
    'WELCOMING': 'Привет!',
    'BYEBYING': 'Пока(',
    'KICK_TEXT': 'Кышь мышь',
}
render_temps()

msg_info_dict = {
            'chat_id': None,
            'name': None,
            'user_id': None,
            'status': None,
            'items': None,
            'time': None,
            'text': None,
        }
try:
    for event in longpoll.listen():
        try:
            if event.from_chat:
                if event.type == VkEventType.MESSAGE_NEW:
                    msg_info_dict = msg_info_write(event)
                    if event.text:
                        request_processing()
                elif event.type_id == VkChatEventType.USER_JOINED:
                    sender(f'{temp_texts["WELCOMING"]}')
                elif event.type_id == VkChatEventType.USER_LEFT:
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
