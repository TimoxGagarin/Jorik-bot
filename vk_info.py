import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.exceptions import ApiError
from config import main_token, GROUP_ID
from Message import Message

EMPTY_KEYBOARD = VkKeyboard.get_empty_keyboard()
chat_session = vk_api.VkApi(token=main_token)
vk = chat_session.get_api()
longpoll = VkLongPoll(chat_session)

group_session = vk_api.VkApi(token=main_token)
longpoll_group = VkBotLongPoll(group_session, GROUP_ID)
upload = VkUpload(vk)

message = Message()
bad_words = set()
