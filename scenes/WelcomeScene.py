import sys
import os
import pygame
sys.path.append(os.path.abspath("."))

from Logger import Logger
from Scene import Scene, create_action_button
from Screen import Screen
from Config import Config, Strings
from ResourceManager import ResourceManager
from SceneManager import SceneManager
from Arduino import Arduino

class WelcomeScene(Scene):
    def __init__(self, arduino):
        Scene.__init__(self)
        self.arduino = arduino

        self.img = Screen.get_instance().create_image(self.get_name())
        if not self.img.is_cached():
            self.img.load(ResourceManager.get("welcome.png"))
            create_action_button(Arduino.BUTTON_1, Strings.get("Go"), self.img.get_surface())
            create_action_button(Arduino.BUTTON_2, Strings.get("Settings"), self.img.get_surface())
            self.img.save()
        self.arduino.register_callback(Arduino.BUTTON_1, self.on_button1)
        self.arduino.register_callback(Arduino.BUTTON_2, self.on_button2)

    def get_name(self):
        return "welcome"

    def show(self):
        Scene.show(self, self.img)
        qr_path = os.path.join(ResourceManager.get_instance().get_folder(), "last_qrcode.png")
        if os.path.exists(qr_path):
            qr = pygame.image.load(qr_path)
            iw, ih = qr.get_size()
            w, h = self.img.size
            l = (w - iw) / 2
            t = h - ih - (h / 6)
            Screen.get_instance().get_window().blit(qr, (l ,t))

            txt = Screen.create_text(Strings.get("Last picture :"), ResourceManager.get(Config.get("font")), Config.get("qrcode")["text_size"], Config.get("text_color"))
            iw, ih = txt.get_size()
            l = (w - iw) / 2
            t -= ih + 5
            Screen.get_instance().get_window().blit(txt, (l ,t))

            Screen.get_instance().update()
        Logger.get_instance().show_msg()

    def on_button1(self):
        if self.shown:
            Logger.log_debug("WelcomScene.on_button1")
            SceneManager.get_instance().show_scene("select_mode")
            return True
        return False

    def on_button2(self):
        if self.shown:
            Logger.log_debug("WelcomScene.on_button2")
            SceneManager.get_instance().show_scene("settings")
            return True
        return False

