import pygame
import os
import numpy

from Logger import Logger

class Image:
    def __init__(self, img_id, size, use_yuv=False):
        self.img_id = img_id
        self.size = size
        self.filename = None
        self.img = None

        self.filename = "cache/%s_%d_%d.png" % (self.img_id, self.size[0], self.size[1])
        if os.path.isfile(self.filename):
            self.img = pygame.image.load(self.filename)

    def is_cached(self):
        return (self.img is not None)

    def load(self, filename):
        if not os.path.isfile(filename):
            raise Exception("File '%s' not found" % filename)
        self.img = pygame.image.load(filename)

    def load_surface(self, surface):
        self.img = surface

    def adapt_to_screen(self):
        self.img = pygame.transform.scale(self.img, self.size)

    def save(self):
        self.adapt_to_screen()
	folder = os.path.dirname(self.filename)
	if not os.path.exists(folder):
	    os.makedirs(folder)
        pygame.image.save(self.img, self.filename)
        Logger.log_debug("Save cache file '%s'" % (self.filename))

    def get_surface(self):
        return self.img
