from commands import *


class Command:

    def __init__(self, command, priority, func):
        self.command = command
        self.priority = priority
        self.func = func

    def __str__(self):
        return self.command

    def this_command(self, message) -> bool:
        return message.text_low.startswith(self.command) and self.compare_statuses(message.status)

    def compare_statuses(self, status):
        return self.priority <= status


vk_commands_list = [
    Command('инфа ', 0, infa),
    Command('кто ', 0, who),
    Command('стикер ', 0, sticker),
    Command('погода ', 0, wheather),
    Command('что такое ', 0, what_it_is),
    #Command('товары', 0, goods),
    Command('команды', 0, commands_list),
    Command('запрети фразу ', 5, ban_phrase),
    Command('разреши фразу ', 5, unban_phrase),
    Command('запрещенные фразы', 5, bad_words_list),
    Command('новое приветствие:', 5, new_greeting),
    Command('новое прощание:', 5, new_byeing),
    Command('новый текст кика:', 5, new_kick_text),
    Command('статус ', 5, give_status),
    Command('статусы', 0, statuses_list),
    Command('кик ', 4, kick),
    Command('обновить', 0, reload_all),
    Command('мне ник ', 1, give_nick),
    Command('ники', 0, nicks_list),
    Command('преды', 0, preds_list),
    Command('брак ', 0, marry_command),
    Command('развод', 0, divorce_command),
    Command('браки', 0, marriages_list),
    Command('котик', 1, send_cat),
    Command('пред ', 4, pred),
    Command('снять пред ', 4, remove_pred),
    Command('рассылка ', 5, mailing_set),
]