class Command:

    def __init__(self, command, priority, func):
        self.command = command
        self.priority = priority
        self.func = func

    def __str__(self):
        return self.command
