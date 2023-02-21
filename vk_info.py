import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType, VkChatEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.exceptions import ApiError
from config import ACCESS_TOKEN, GROUP_ID
from Message import Message
from dotenv import load_dotenv

chat_session = vk_api.VkApi(token=ACCESS_TOKEN)
vk = chat_session.get_api()
longpoll_chat = VkLongPoll(chat_session)

group_session = vk_api.VkApi(token=ACCESS_TOKEN)
longpoll_group = VkBotLongPoll(group_session, GROUP_ID)
upload = VkUpload(vk)

message = Message()
bad_words = set()
