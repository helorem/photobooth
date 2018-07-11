import pygame
import time
import threading
import io
import traceback
import PIL

from Logger import Logger
from CacheImage import Image
from Config import Config, Strings

class Screen:
    def __init__(self):
        self.camera = None
        self.w = 0
        self.h = 0
        #self.preview_size = (Config.get("preview")["w"], Config.get("preview")["h"])
        self.window = None
        self.preview_enabled = False
        self.img = None
        #self.preview_thread = None
        self.callbacks = {}
        self.initialized = False
        self.overlays = {}

    def get_size(self):
        return (self.w, self.h)

    def _set_display(self):
        if not Config.get("desktop_mode", False):
            if not self.w:
                self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, 16)
            else:
                self.window = pygame.display.set_mode((self.w, self.h), pygame.FULLSCREEN, 16)
        else:
            self.window = pygame.display.set_mode((640, 480), 0, 32)

    def init(self, camera):
        self.camera = camera
        pygame.init()
        pygame.mouse.set_visible(False)
        self._set_display()
        self.w, self.h = self.window.get_size()

        # Write loading
        myfont = pygame.font.SysFont("monospace", 32)
        label = myfont.render(Strings.get("Loading..."), 1, (255, 255, 0))
        lw, lh = label.get_rect().size
        self.window.blit(label, ((self.w - lw) / 2, (self.h - lh) / 2))
        self.update()

        Logger.log_debug("Screen initialized with resolution %dx%d" % (self.w, self.h))
        self.initialized = True

    def close(self):
        pygame.quit()

    def get_window(self):
        return self.window

    def update(self):
        pygame.display.update()

    def register_callback(self, callback_id, callback):
        if callback_id not in self.callbacks:
            self.callbacks[callback_id] = []
        self.callbacks[callback_id].append(callback)

    def _call_callbacks(self, callback_id):
        if callback_id in self.callbacks:
            for callback in self.callbacks[callback_id]:
                callback()

    def show_img(self, img, do_update=True):
        if img != self.img:
            self.img = img
            if not self.preview_enabled:
                self.window.blit(self.img.get_surface(), (0, 0))
                if do_update:
                    self.update()
            elif img:
                overlay = self.camera.add_overlay(img)
                self.overlays[img] = overlay

    def hide_img(self, img):
        if self.preview_enabled:
            if img in self.overlays:
                self.overlays[img].close()
                del self.overlays[img]

    def start_preview(self):
        if not self.preview_enabled:
            self.camera.start_preview()
            self.preview_enabled = True
            self._call_callbacks("on_preview_starts")

    def stop_preview(self):
        if self.preview_enabled:
            self.preview_enabled = False
            for overlay in self.overlays.values():
                overlay.close()
            self.camera.stop_preview()
            if not Config.get("desktop_mode", False):
                self._set_display()
            pygame.display.update()
            Logger.log_debug("Preview stopped")

    def create_image(self, img_id, preview=False):
        img = None
        img = Image(img_id, (self.w, self.h))
        return img

    def create_empty_image(self, preview=False):
        img = None
        img = Image(None, (self.w, self.h))
        base_img = pygame.Surface(img.size, pygame.SRCALPHA, 32)
        base_img = base_img.convert_alpha()
        img.load_surface(base_img)
        return img

    @staticmethod
    def create_text(text, font, size, color):
        myfont = None
        if font:
            myfont = pygame.font.Font(font, size)
        else:
            myfont = pygame.font.SysFont("truetype", size)
        surface = myfont.render(text, 1, color)
        return surface

    @staticmethod
    def create_button(filename, text, text_color, font, font_size):
        surface = pygame.image.load(filename)
        surf_text = Screen.create_text(text, font, font_size, text_color)
        tw, th = surf_text.get_size()
        bw, bh = surface.get_size()
        surface.blit(surf_text, ((bw - tw) / 2, (bh - th) / 2))
        return surface

    _instance = None
    @staticmethod
    def get_instance():
        if not Screen._instance:
            Screen._instance = Screen()
        return Screen._instance

 
