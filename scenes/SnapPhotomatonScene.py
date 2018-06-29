import time
import sys
import os
import pygame
import PIL.Image
sys.path.append(os.path.abspath("."))

from Screen import Screen
from scenes.SnapScene import SnapScene
from Logger import Logger
from Config import Config, Strings
from Scene import Scene
from ResourceManager import ResourceManager
from SceneManager import SceneManager

class SnapPhotomatonScene(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.callback = self._default_cb

        self.wait_img = Screen.get_instance().create_image(self.get_name() + "_wait")
        if not self.wait_img.is_cached():
            img = Screen.create_button(ResourceManager.get("empty.png"),
                                                    Strings.get("Please wait..."),
                                                    Config.get("text_color"),
                                                    ResourceManager.get(Config.get("font")),
                                                    100)
            self.wait_img.load_surface(img)
            self.wait_img.save()

        self.nb_imgs = len(Config.get("photomaton")["placeholders"])
        self.one_more_imgs = []
        for i in xrange(self.nb_imgs):
            self.one_more_imgs.append(Screen.get_instance().create_image(self.get_name() + "_one_more%d" % i))
            if not self.one_more_imgs[i].is_cached():
                img = Screen.create_button(ResourceManager.get("empty.png"),
                                                        Strings.get("Encore une... (%d / %d)" % (i + 1, self.nb_imgs)),
                                                        Config.get("text_color"),
                                                        ResourceManager.get(Config.get("font")),
                                                        100)
                self.one_more_imgs[i].load_surface(img)
                self.one_more_imgs[i].save()

    def get_name(self):
        return "photomaton"

    def show(self, callback=None):
        Scene.show(self)
        if callback:
            self.callback = callback
        self.img = PIL.Image.open(ResourceManager.get(Config.get("photomaton")["template"]))
        self.img_counter = 0
        SceneManager.get_instance().show_scene("snap", self._process_img)

    def _process_img(self, path, img):
        if self.img_counter < self.nb_imgs - 1:
            Scene.show(self, self.one_more_imgs[self.img_counter])
        else:
            Scene.show(self, self.wait_img)
        start_time = time.time()

        Logger.log_debug("process img %d / %d" % (self.img_counter, len(Config.get("photomaton")["placeholders"])))
        rect = Config.get("photomaton")["placeholders"][self.img_counter]
        pic = PIL.Image.open(path)
        pic.thumbnail((rect["w"], rect["h"]))
        self.img.paste(pic, (rect["x"], rect["y"]))

        self.img_counter += 1
        if self.img_counter < self.nb_imgs:
            elapsed = time.time() - start_time
            to_wait = Config.get("photomaton")["wait"] - elapsed
            if to_wait > 0:
                time.sleep(to_wait)
            SceneManager.get_instance().show_scene("snap", self._process_img)
        else:
            self.callback(self.img)

    def _default_cb(self, img):
        now = time.strftime("%Y-%m-%d_%H.%M.%S") #get the current date and time for the start of the filename
        filename = "photomaton_%s.jpg" % now
        path = os.path.join(SnapScene.get_folder(), filename)
        self.img.save(path)

        if not os.path.isfile(path):
            Logger.log_error("File '%s' was not created" % path)
        else:
            img = Screen.get_instance().create_image("tmp")
            img.load(path)
            img.adapt_to_screen()
            Scene.show(self, img)

            SnapScene.create_qrcode(filename, os.path.join(ResourceManager.get_instance().get_folder(), "last_qrcode.png"))
        to_wait = Config.get("picture_show_delay")
        if to_wait > 0:
            time.sleep(to_wait)
        SceneManager.get_instance().show_main_scene()


