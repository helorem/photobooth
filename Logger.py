
class Logger:
    _instance = None

    def __init__(self):
        self.msgs = []

    def show_msg(self):
        if self.msgs:
            from Screen import Screen

            if Screen.get_instance().initialized:
                pos = 0
                for msg in self.msgs:
                    txt = Screen.create_text(msg, None, 20, (255, 0, 0))
                    Screen.get_instance().get_window().blit(txt, (10, pos + 10))
                    pos += txt.get_size()[1] + 5
                Screen.get_instance().update()

    @staticmethod
    def get_instance():
        if not Logger._instance:
            Logger._instance = Logger()
        return Logger._instance

    @staticmethod
    def log_debug(msg):
        print "DEBUG : %s" % msg

    @staticmethod
    def log_info(msg):
        print "INFO : %s" % msg

    @staticmethod
    def log_warning(msg):
        txt = "WARNING : %s" % msg
        print txt
        Logger.get_instance().msgs.append(txt)
        Logger.get_instance().show_msg()


    @staticmethod
    def log_error(msg):
        txt = "ERROR : %s" % msg
        print txt
        Logger.get_instance().msgs.append(txt)
        Logger.get_instance().show_msg()

