from random import randint
from config import temp_texts, mailing, CHAT_ID, GROUP_ID, BOT_NAME
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
from vk_info import *


# get name in VK
def get_name(user_id):
    try:
        return f"[id{user_id}|{vk.users.get(user_ids=user_id)[0]['first_name']}]"
    except IndexError:
        return "Участника с таким именем не существует"


# get surname in VK
def get_surname(user_id):
    try:
        return f"[id{user_id}|{vk.users.get(user_ids=user_id)[0]['last_name']}]"
    except IndexError:
        return "Участника с таким именем не существует"


# Choose VK-name or nick
def name_or_nick(user_id):
    to = get_name(user_id)
    if check_nick(user_id=user_id):
        if check_nick(user_id=user_id).split('|')[1] != ']':
            to = check_nick(user_id=user_id)
    return to


def group_name_anchor():
    return f'[club{GROUP_ID}|@{chat_session.method("groups.getById", {"group_id": GROUP_ID})[0]["screen_name"]}]'


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
                temp_texts[temp] = moji.emojize(line[len(temp) + 1:]).replace('\n', '').encode("ascii").decode("utf-8")
            except UnicodeEncodeError:
                temp_texts[temp] = moji.emojize(line[len(temp) + 1:]).replace('\n', '')


# Function have rendering temp to temps file
def render_new_temps():
    with open('temp_texts.txt', 'w') as file:
        try:
            [file.write(str(f'{k}: {moji.demojize(v)}\n')) for k, v in temp_texts.items()]
        except TypeError:
            pass


# Function check admin permissions
def reload_admins(event):
    people_items = chat_session.method('messages.getConversationMembers', {'peer_id': event.peer_id})['items']
    for member in people_items:
        try:
            if member['member_id'] < 0:
                continue
            if member['is_admin']:
                set_status(user_id=member['member_id'], status=5)
                continue
        except KeyError:
            if check_status(user_id=member['member_id']) == 5:
                set_status(user_id=member['member_id'], status=0)
                continue


def reg_all(event):
    members = chat_session.method('messages.getConversationMembers', {'peer_id': event.peer_id})['profiles']
    users_ids = users()
    for member in members:
        if member['id'] not in users_ids:
            remove_from_db(user_id=member['id'])
    [register(user_id=member['id']) for member in members]


def get_id(name, event) -> bool:
    people_profiles = chat_session.method('messages.getConversationMembers', {'peer_id': event.peer_id})['profiles']
    for member in people_profiles:
        if ((member['last_name'].lower() == name.lower()) or (member['first_name'].lower() == name.lower()) or (
                member['first_name'].lower() + ' ' + member['last_name'].lower() == name.lower())) or str(
                member['id']) == str(name.split('|')[0].replace('[id', '')):
            return member['id']


# Function send text message
def sender(text='', keyboard=None, photo=None, wall_post='None', disable_mentions=1, template=None):
    post = {
        'chat_id': CHAT_ID,
        'random_id': 0,
        'disable_mentions': disable_mentions,
    }
    if keyboard is not None:
        post['keyboard'] = keyboard
    if text != '':
        post['message'] = text
    if wall_post != '':
        post['attachment'] = wall_post
    if photo is not None:
        photo_info = upload_photo(BytesIO(requests.get(photo).content))
        post['attachment'] = f'photo{photo_info[0]}_{photo_info[1]}_{photo_info[2]}'
    if template is not None:
        post['template'] = template
    chat_session.method('messages.send', post)


# Function send sticker from getting number
def send_stick(number):
    chat_session.method('messages.send', {'chat_id': message.chat_id, 'sticker_id': number, 'random_id': 0})


# Functions send photo
def upload_photo(photo):
    response = upload.photo_messages(photo)[0]
    return response['owner_id'], response['id'], response['access_key']


# Function kick user from the chat
def kick_user(user_id):
    remove_from_db(user_id=user_id)
    chat_session.method('messages.removeChatUser', {'chat_id': message.chat_id, 'user_id': user_id, 'random_id': 0})


def add_pred_and_check(user_id):
    add_pred(user_id=user_id)
    to = name_or_nick(user_id)
    sender(f'{to} получает предупреждение ({check_preds(user_id=user_id)}/{temp_texts["PREDS"]})')
    if check_preds(user_id=user_id) == temp_texts['PREDS']:
        kick_user(user_id)


def new_thread(func, args=[]):
    stream = Thread(target=func, args=args)
    stream.start()
    stream.join()


#Function have checking target of message
def for_bot() -> bool:
    return message.text_low.startswith(f'{BOT_NAME},')


# Function kick user if he wrote bad word from the list:
def check_msg4bad_words():
    if message.status < 4 and message.user_id != -GROUP_ID:
        [add_pred_and_check(message.user_id) if word in bad_words else None for word in message.text_low.split(' ')]
