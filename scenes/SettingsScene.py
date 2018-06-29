import sys
import os
sys.path.append(os.path.abspath("."))

from Logger import Logger
from Scene import Scene, FormButton, Form, create_action_button
from Config import Strings
from ResourceManager import ResourceManager
from SceneManager import SceneManager
from Screen import Screen
from Arduino import Arduino

class SettingsScene(Scene):
    def __init__(self, arduino):
        Scene.__init__(self)
        self.arduino = arduino

        self.img = Screen.get_instance().create_image(self.get_name())
        if not self.img.is_cached():
            self.img.load(ResourceManager.get("empty.png"))
            create_action_button(Arduino.BUTTON_1, Strings.get("Ok"), self.img.get_surface())
            create_action_button(Arduino.BUTTON_2, Strings.get("Next"), self.img.get_surface())
            self.img.save()
        arduino.register_callback(Arduino.BUTTON_1, self.on_button1)
        arduino.register_callback(Arduino.BUTTON_2, self.on_button2)

        w, h = Screen.get_instance().get_size()
        self.menu = Form((w, h))
        self.menu.add_item(FormButton(Strings.get("Clean Cache"), self._action_clean_cache))
        self.menu.add_item(FormButton(Strings.get("Shutdown"), self._action_shutdown))
        self.menu.add_item(FormButton(Strings.get("Back"), self._action_back))

        self.menu.cache(self.get_name(), self.img)

    def get_name(self):
        return "settings"

    def show(self):
        Scene.show(self, self.menu.get_img(self.get_name()))

    def on_button1(self):
        if self.shown:
            self.menu.get_selected().do_action()
            return True
        return False

    def on_button2(self):
        if self.shown:
            self.menu.select_next()
            self.show()
            return True
        return False

    def _action_back(self):
        SceneManager.get_instance().show_main_scene()

    def _action_shutdown(self):
        Logger.log_info("Quit")
        SceneManager().get_instance().stop()
        os.system("sudo halt")

    def _action_clean_cache(self):
        folder = "./cache"
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            try:
                os.unlink(path)
            except Exception as ex:
                Logger.log_warning(ex)
        self._action_shutdown()

