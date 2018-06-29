import time
import sys
import os
import qrencode
import threading
import pygame
sys.path.append(os.path.abspath("."))

from Camera import Camera
from Screen import Screen
from Logger import Logger
from Config import Config, Strings
from Scene import Scene
from ResourceManager import ResourceManager
from SceneManager import SceneManager
from Arduino import Arduino

class SnapScene(Scene):
    def __init__(self, arduino, camera):
        Scene.__init__(self)
        self.arduino = arduino
        self.camera = camera
        self.timer = None
        self.current_step = 0
        self.callback = self._default_cb

        self.cheese_img = Screen.get_instance().create_image(self.get_name() + "_cheese")
        if not self.cheese_img.is_cached():
            img = Screen.create_button(ResourceManager.get("empty.png"),
                                                    Strings.get("Cheese"),
                                                    Config.get("text_color"),
                                                    ResourceManager.get(Config.get("font")),
                                                    100)
            self.cheese_img.load_surface(img)
            self.cheese_img.save()

        self.wait_img = Screen.get_instance().create_image(self.get_name() + "_wait")
        if not self.wait_img.is_cached():
            img = Screen.create_button(ResourceManager.get("empty.png"),
                                                    Strings.get("Please wait..."),
                                                    Config.get("text_color"),
                                                    ResourceManager.get(Config.get("font")),
                                                    100)
            self.wait_img.load_surface(img)
            self.wait_img.save()

        self.imgs = []
        wait_before = Config.get("wait_before_snap")
        for i in xrange(wait_before, 0, -1):
            cache_img = Screen.get_instance().create_image("%s_%d" % (self.get_name(), i), True)
            if not cache_img.is_cached():
                base_img = Screen.get_instance().create_empty_image(True)
                cache_img.load_surface(base_img.img)

                img = Screen.create_text(str(i), None, 200, (255, 0, 0))
                iw, ih = img.get_size()
                w, h = base_img.size

                cache_img.img.blit(img, (10, 10))
                cache_img.img.blit(img, (w - iw - 10, 10))
                cache_img.img.blit(img, (10, h - ih - 10))
                cache_img.img.blit(img, (w - iw - 10, h - ih - 10))

                cache_img.save()
            self.imgs.append(cache_img)

        Screen.get_instance().register_callback("on_preview_starts", self._on_preview_starts)

    def get_name(self):
        return "snap"

    def show(self, callback=None):
        Scene.show(self, self.wait_img)
        self.current_step = 0
        if callback:
            self.callback = callback
        else:
	    self.callback = self._default_cb
        Screen.get_instance().start_preview()

    def _next_step(self):
        if self.shown:
            if self.current_step >= len(self.imgs):
                self.timer = None
                self.snap()
            else:
                Scene.show(self, self.imgs[self.current_step])
                self.current_step += 1
                self.timer = threading.Timer(1.0, self._next_step)
                self.timer.start()

    def _on_preview_starts(self):
        if self.shown:
            self._next_step()

    def _before_shot(self):
        if self.shown:
            self.arduino.flash_on()

    def _after_shot(self):
        if self.shown:
            self.arduino.flash_off()
            Scene.show(self, self.wait_img)

    def snap(self):
        now = time.strftime("%Y-%m-%d_%H.%M.%S") #get the current date and time for the start of the filename
        filename = "%s.jpg" % now
        path = os.path.join(SnapScene.get_folder(), filename)

        Screen.get_instance().stop_preview()
        Scene.show(self, self.cheese_img)
        img = self.camera.snapshot(path, {
                Camera.CB_BEFORE_SHOT : self._before_shot,
                Camera.CB_AFTER_SHOT : self._after_shot
                })

        self.callback(path, img)
        return img

    def _default_cb(self, path, img):
        Screen.get_instance().get_window().blit(img, (0, 0))
        Screen.get_instance().update()
        start_time = time.time()

        if not os.path.isfile(path):
            Logger.log_error("File '%s' was not created" % path)
        else:
            SnapScene.create_qrcode(os.path.basename(path), os.path.join(ResourceManager.get_instance().get_folder(), "last_qrcode.png"))
        elapsed = time.time() - start_time
        to_wait = Config.get("picture_show_delay") - elapsed
        if to_wait > 0:
            time.sleep(to_wait)
        SceneManager.get_instance().show_main_scene()

    @staticmethod
    def get_folder():
        for folder in Config.get("snapshot")["folders"]:
            if os.path.exists(folder):
                return folder
        return "."

    @staticmethod
    def create_qrcode(filename, target_file):
        if not Config.get("desktop_mode", False):
            # Not working in desktop mode because qrcode is deprecated
            url = Config.get("url") + filename
            _, sz, img = qrencode.encode(data=url, level=1)
            qr_zoom = Config.get("qrcode")["zoom"]
            img = img.resize((sz * qr_zoom, sz * qr_zoom))
            img.save(target_file)

