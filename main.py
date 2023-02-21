import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.exceptions import ApiError
from config import temp_texts, mailing, CHAT_ID, GROUP_ID
from Message import Message
from UseDatabase import register, remove_from_db
import datetime as dt
import requests
from vk_funcs import *
from vk_info import *
from Command import Command, vk_commands_list


def listen_group():
    for event in longpoll_group.listen():
        if event.type == VkBotEventType.WALL_POST_NEW and mailing:
            id_ = event.object['id']
            owner_id_ = event.group_id
            wall_id = f'wall-{owner_id_}_{id_}'
            vk_funcs.sender('Новый пост в группе!', wall_post=wall_id)


def listen_chat():
    for event in longpoll_chat.listen():
        if event.from_chat:
            if event.type == VkEventType.MESSAGE_NEW:
                message.update(event, get_name(event.user_id), get_surname(event.user_id),
                            check_nick(user_id=event.user_id), event.text,
                            dt.datetime.now().strftime("%d.%m.%Y] (%H:%M"), check_status(user_id=event.user_id),
                            chat_session.method('messages.getConversationMembers', {'peer_id': event.peer_id})['items'])
                register(user_id=event.user_id)
                if event.text != '':
                    check_msg4bad_words()
                    if for_bot():
                        message.text = message.text[6:].strip()
                        message.text_low = message.text.lower()
                        to = name_or_nick(message.user_id)
                        for command in vk_commands_list:
                            if command.this_command(message):
                                if not command.compare_statuses(message.status):
                                    sender(f'{message.name}, отказано в доступе ({message.status}<{command.priority})')
                                    break
                                args = list()
                                for arg in command.func.__code__.co_varnames[:command.func.__code__.co_argcount]:
                                    args.append(eval(arg))
                                new_thread(command.func, args)
                                break
            if event.type_id == VkChatEventType.USER_JOINED:
                sender(f'{temp_texts["WELCOMING"]}')
                register(user_id=message.user_id)
            elif event.type_id == VkChatEventType.USER_LEFT:
                remove_from_db(user_id=message.event.user_id)
                sender(f'{temp_texts["BYEBYING"]}')
            elif event.type_id == VkChatEventType.USER_KICKED:
                remove_from_db(user_id=message.event.user_id)
                sender(f'{temp_texts["KICK_TEXT"]}')


if __name__ == '__main__':
    render_bad_words()
    render_temps()
    new_thread(listen_chat)
    new_thread(listen_group)
