from Arduino import Arduino
from Config import Config
from Screen import Screen
from ResourceManager import ResourceManager
from Logger import Logger
import pygame
import os

class Scene:
    def __init__(self):
        self.shown = False

    def render(self):
        # override
        pass

    def get_name(self):
        # override
        return None

    def show(self, img=None, update=True):
        self.shown = True
        if img:
            Screen.get_instance().show_img(img, update)

    def hide(self):
        self.shown = False

class FormButton:
    def __init__(self, name, action=None, param=None):
        self.name = name
        self.action = action
        self.param = param

        img_file = ResourceManager.get("%s.png" % name)
        img_file_sel = ResourceManager.get("%s_sel.png" % name)

        if img_file and os.path.isfile(img_file):
            self.img = pygame.image.load(img_file)
            if img_file_sel and os.path.isfile(img_file_sel):
                self.img_sel = pygame.image.load(img_file_sel)
            else:
                self.img_sel = self.img
        else:
            # Generate img
            button_font = Config.get("form_buttons")["normal"]["font"]
            button_font_size = Config.get("form_buttons")["normal"]["font_size"]
            button_text_color = Config.get("form_buttons")["normal"]["text_color"]
            self.img = Screen.create_text(name, ResourceManager.get(button_font), button_font_size, button_text_color)

            button_font = Config.get("form_buttons")["selected"]["font"]
            button_font_size = Config.get("form_buttons")["selected"]["font_size"]
            button_text_color = Config.get("form_buttons")["selected"]["text_color"]
            self.img_sel = Screen.create_text(name, ResourceManager.get(button_font), button_font_size, button_text_color)

        self.is_selected = False
        self.need_rendering = False

    def get_size(self):
        return self.img.get_size()

    def select(self, is_selected):
        self.is_selected = is_selected
        self.need_rendering = True

    def render(self, img, pos):
        img.blit(self.get_img(), pos)

    def get_img(self):
        if self.is_selected and self.img_sel:
            return self.img_sel
        return self.img

    def do_action(self):
        if self.action:
            if self.param:
                self.action(self.param)
            else:
                self.action()

class Form:
    def __init__(self, size, pos=(0, 0)):
        self.button_margin = Config.get("button_margin")

        self.pos = pos
        self.size = size
        self.items = []
        self.current_selection = 0
        self.imgs = {}

    def cache(self, scene_name, img):
        for i in xrange(0, len(self.items)):
            img_id = "%s_form%d" % (scene_name, i)
            if img_id not in self.imgs:
                img2 = Screen.get_instance().create_image(img_id)
                if not img2.is_cached():
                    img2.load_surface(img.get_surface().copy())
                    self.update(img2.get_surface())
                    img2.save()
                self.imgs[img_id] = img2
            self.select_next()

    def get_img(self, scene_name):
        img_id = "%s_form%d" % (scene_name, self.current_selection)
        return self.imgs[img_id]


    def select_next(self):
        self.get_selected().select(False)
        self.current_selection += 1
        if self.current_selection == len(self.items):
            self.current_selection = 0
        self.get_selected().select(True)

    def get_selected(self):
        return self.items[self.current_selection]

    def add_item(self, item):
        if len(self.items) == 0:
            item.select(True)
        self.items.append(item)

    def update(self, img):
        w, h = self.size
        item = self.get_selected()
        iw, ih = item.get_size()
        x = int((w - iw) / 2)
        y = int((h - ih) / 2)
        y2 = int((h + ih) / 2)
        item.render(img, (self.pos[0] + x, self.pos[1] + y))
        for i in xrange(1, len(self.items)):
            looping = False
            if self.current_selection - i >= 0:
                item = self.items[self.current_selection - i]
                iw, ih = item.get_size()
                y -= self.button_margin + ih
                if y >= 0:
                    x = int((w - iw) / 2)
                    item.render(img, (self.pos[0] + x, self.pos[1] + y))
                    looping = True

            if self.current_selection + i < len(self.items):
                item = self.items[self.current_selection + i]
                iw, ih = item.get_size()
                y2 += self.button_margin
                if y2 + ih <= h - self.button_margin:
                    x = int((w - iw) / 2)
                    item.render(img, (self.pos[0] + x, self.pos[1] + y2))
                    y2 += ih
                    looping = True
            if not looping:
                break
        return img

def create_action_button(button_id, text, img):
    button_font = Config.get("buttons")["font"]
    button_font_size = Config.get("buttons")["font_size"]
    button_img = Config.get("buttons")["img"]
    button_margin = Config.get("button_margin")
    button_text_color = Config.get("buttons")["text_color"]

    button = Screen.create_button(ResourceManager.get(button_img), text, button_text_color, ResourceManager.get(button_font), button_font_size)

    w, h = img.get_size()
    bw, bh = button.get_size()
    if button_id == Arduino.BUTTON_1:
        img.blit(button, (w - (bw + button_margin), h - (bh + button_margin)))
    elif button_id == Arduino.BUTTON_2:
        img.blit(button, (button_margin, h - (bh + button_margin)))

