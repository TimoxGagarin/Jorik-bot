from config import temp_texts
import vk_api


class Message:

    def __init__(self, event, name, surname, nick, text, time, status, items):
        self.event = event
        self.chat_id = event.chat_id
        self.user_id = event.user_id
        self.items = items

        self.name = name
        self.surname = surname
        self.nick = nick

        self.time = time
        self.status = status
        self.text_low = text.lower()
        self.text = text
        if self.status == None:
            self.status = 0
            self.status_text = 'User'
        if self.status != 0:
            self.status_text = temp_texts['STATUS' + str(self.status)]
        else:
            self.status_text = 'User'

    def __repr__(self):
        return f"{self.time} [{self.status_text}] {self.name}: {self.text}"
