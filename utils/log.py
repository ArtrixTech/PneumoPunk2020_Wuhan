import time


class Log:

    def __init__(self, module_name):
        self.module_name = module_name
        self.level = 0

    def log(self, message):

        text = ""
        for i in range(self.level):
            text += "  "
        if self.level == 0:
            text += '[ %s ] %t'.replace('%s', self.module_name).replace('%t', time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                            time.localtime()))
        text += ' %s'.replace('%s', message)
        self.level += 1
        print(text)

    def finished(self):
        self.level -= 1
