import os
import time

from Logger import Logger
from Config import Config, Strings
Config.get_instance().load("./assets/config.json")

if not Config.get("desktop_mode", False):
    from Arduino import Arduino
    from Camera import Camera
else:
    from Arduino import FakeArduino as Arduino
    from Camera import FakeCamera as Camera

from ResourceManager import ResourceManager
from Screen import Screen
from SceneManager import SceneManager
from scenes.WelcomeScene import WelcomeScene
from scenes.SelectModeScene import SelectModeScene
from scenes.SettingsScene import SettingsScene
from scenes.SnapScene import SnapScene
from scenes.SnapPhotomatonScene import SnapPhotomatonScene
from scenes.SnapSpecialScene import SnapSpecialScene
from scenes.SelectEffectScene import SelectEffectScene

def quit():
    Logger.log_info("Quit")
    SceneManager().get_instance().stop()
    return True

if __name__ == "__main__":
    Strings.get_instance().load(ResourceManager.get(Config.get("strings_file")))
    camera = Camera()
    arduino = Arduino()
    Screen.get_instance().init(camera)
    try:
        camera.start()
        arduino.start()
        try:
            arduino.register_callback(Arduino.BUTTON_3, quit, Config.get("halt_delay"))

            sm = SceneManager().get_instance()
            sm.add_scene(WelcomeScene(arduino))
            sm.add_scene(SettingsScene(arduino))
            sm.add_scene(SelectModeScene(arduino))
            sm.add_scene(SnapScene(arduino, camera))
            sm.add_scene(SnapPhotomatonScene())
            sm.add_scene(SnapSpecialScene(arduino, camera))
            sm.add_scene(SelectEffectScene(arduino))
            sm.set_main_scene("welcome")
            sm.start()
        finally:
            arduino.stop()
            arduino.close()
            camera.stop()
    finally:
        Screen.get_instance().close()
