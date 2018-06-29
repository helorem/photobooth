import time
import sys
import os
import PIL.Image
sys.path.append(os.path.abspath("."))

from scenes.SnapScene import SnapScene

from Scene import Scene
from Config import Config
from Screen import Screen
from Logger import Logger
from SceneManager import SceneManager
from ResourceManager import ResourceManager

class SnapSpecialScene(SnapScene):
    def __init__(self, arduino, camera):
        SnapScene.__init__(self, arduino, camera)

        self.selected_overlay = None

        overlays = []
        for item in Config.get("special_effects"):
            overlays.append(item["id"])

        self.overlay_imgs = {}
        for overlay in overlays:
            self.overlay_imgs[overlay] = []
            for i in xrange(len(self.imgs)):
                base_img = self.imgs[i]
                cache_img = Screen.get_instance().create_image("%s_%s_%d" % (self.get_name(), overlay, i), True)
                if not cache_img.is_cached():
                    cache_img.load(os.path.join(ResourceManager.get_instance().get_folder(), overlay))
                    cache_img.adapt_to_screen()
                    cache_img.img.blit(base_img.img, (0, 0))
                    cache_img.save()
                self.overlay_imgs[overlay].append(cache_img)

    def get_name(self):
        return "snap_special"

    def show(self, overlay):
        self.selected_overlay = overlay
        self.imgs = self.overlay_imgs[overlay]
        SnapScene.show(self)

    def _default_cb(self, path, img):

        now = time.strftime("%Y-%m-%d_%H.%M.%S") #get the current date and time for the start of the filename
        filename = "special_%s.jpg" % now
        new_path = os.path.join(SnapScene.get_folder(), filename)

        img = PIL.Image.open(path)
        pic = PIL.Image.open(ResourceManager.get(self.selected_overlay))
        img.paste(pic, (0, 0), pic)
        img.save(new_path)

        if not os.path.isfile(path):
            Logger.log_error("File '%s' was not created" % path)
        else:
            img = Screen.get_instance().create_image("tmp")
            img.load(new_path)
            img.adapt_to_screen()
            Scene.show(self, img)

            SnapScene.create_qrcode(filename, ResourceManager.get("last_qrcode.png"))
        to_wait = Config.get("picture_show_delay")
        if to_wait > 0:
            time.sleep(to_wait)
        SceneManager.get_instance().show_main_scene()

