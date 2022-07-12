from config import temp_texts


class Message:

    def __init__(self, event, name, surname, nick, text, status, items):
        self.event = event
        self.chat_id = event.chat_id
        self.user_id = event.user_id
        self.items = items
        
        self.name = name
        self.surname = surname
        self.nick = nick

        self.status = status
        self.text_low = text.lower()
        self.text = text

        if self.status is None:
            self.status = 0
            self.status_text = 'User'
        if self.status != 0:
            self.status_text = temp_texts['STATUS' + str(self.status)]
        else:
            self.status_text = 'User'
