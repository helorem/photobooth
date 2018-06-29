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

class SelectModeScene(Scene):
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

        self.menu = Form(self.img.get_surface().get_size())
        self.menu.add_item(FormButton("mode_simple", self._snap_simple))
        self.menu.add_item(FormButton("mode_photomaton", self._snap_photomaton))
        self.menu.add_item(FormButton("mode_special", self._snap_special))
        self.menu.cache(self.get_name(), self.img)

    def get_name(self):
        return "select_mode"

    def show(self):
        Scene.show(self, self.menu.get_img(self.get_name()))

    def on_button1(self):
        if self.shown:
            Logger.log_debug("SelectModeScene.on_button1")
            self.menu.get_selected().do_action()
            return True
        return False

    def on_button2(self):
        if self.shown:
            Logger.log_debug("SelectModeScene.on_button2")
            self.menu.select_next()
            self.show()
            return True
        return False

    def _snap_simple(self):
            SceneManager.get_instance().show_scene("snap")

    def _snap_photomaton(self):
            SceneManager.get_instance().show_scene("photomaton")

    def _snap_special(self):
            SceneManager.get_instance().show_scene("select_effect")


