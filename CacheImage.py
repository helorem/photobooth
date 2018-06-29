import pygame
import os
import numpy

from Logger import Logger

def rgb2yuv(r, g, b):
    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = -0.1687 * r - 0.3313 * g + 0.5 * b + 128
    v = 0.5 * r - 0.4187 * g - 0.0813 * b + 128
    y = max(min(255, int(y)), 0)
    u = max(min(255, int(u)), 0)
    v = max(min(255, int(v)), 0)
    return (y, u ,v)

class Image:
    def __init__(self, img_id, size, use_yuv=False):
        self.img_id = img_id
        self.size = size
        self.filename = None
        self.img = None
        self.yuv_filename = None
        self.yuv_img = None

        self.filename = "cache/%s_%d_%d.png" % (self.img_id, self.size[0], self.size[1])
        if os.path.isfile(self.filename):
            self.img = pygame.image.load(self.filename)

        if use_yuv:
            self.yuv_filename = "cache/%s_%d_%d.yuv" % (self.img_id, self.size[0], self.size[1])
            if os.path.isfile(self.yuv_filename):
                with open(self.yuv_filename, "rb") as fd:
                    self.yuv_img = fd.read()

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
        if self.yuv_filename:
            self._generate_yuv(self.img)

    def get_yuv(self):
        return self.yuv_img

    def get_surface(self):
        return self.img

    def _generate_yuv(self, img):
        Logger.log_info("Processing YUV '%s'..." % (self.yuv_filename))
        alphas = pygame.surfarray.pixels_alpha(img)
        pix = pygame.surfarray.array3d(img)
        w, h = img.get_size()
        yuv_img = bytearray(w * h * 4)
        for (col, row), alpha in numpy.ndenumerate(alphas):
            pos = ((row * w) + col) * 4
            if alpha:
                r, g, b = pix[col, row]
                y, u, v = rgb2yuv(r, g, b)
                yuv_img[pos] = 1
                yuv_img[pos + 1] = y
                yuv_img[pos + 2] = u
                yuv_img[pos + 3] = v
            else:
                yuv_img[pos] = 0
                yuv_img[pos + 1] = 0
                yuv_img[pos + 2] = 0
                yuv_img[pos + 3] = 0
        with open(self.yuv_filename, "wb") as fd:
            fd.write(yuv_img)
        Logger.log_debug("Save yuv cache file '%s'" % (self.yuv_filename))
        with open(self.yuv_filename, "rb") as fd:
            self.yuv_img = fd.read()

