import time
import pygame
import numpy as np
import PIL

from Logger import Logger
from Config import Config

class Camera:
    CB_BEFORE_SHOT = 1
    CB_AFTER_SHOT = 2

    def __init__(self):
        self.camera = None
        self.w = Config.get("snapshot")["w"]
        self.h = Config.get("snapshot")["h"]

    def start(self):
        import picamera
        self.camera = picamera.PiCamera()
        self.camera.hflip = True # mirror

    def stop(self):
        if self.camera:
            self.camera.close()

    def set_resolution(self, res):
        self.camera.resolution = res

    def _callback(self, callbacks, event):
        if event in callbacks:
            callbacks[event]()

    def start_preview(self):
        self.camera.start_preview()

    def stop_preview(self):
        self.camera.stop_preview()

    def add_overlay(self, img):
        pil_img = PIL.Image.open(img.filename)
        overlay_img = PIL.Image.new('RGBA', (
            ((pil_img.size[0] + 31) // 32) * 32,
            ((pil_img.size[1] + 15) // 16) * 16,
        ))
        overlay_img.paste(pil_img, (0, 0))
        overlay = self.camera.add_overlay(overlay_img.tobytes(), overlay_img.size, format="rgba")
        overlay.alpha = 255
        overlay.layer = 3
        return overlay

    def snapshot(self, filename, callbacks):
        from picamera.array import PiRGBArray
        rawCapture = PiRGBArray(self.camera)
        self._callback(callbacks, Camera.CB_BEFORE_SHOT)
        self.camera.capture(rawCapture, format="rgb")
        self._callback(callbacks, Camera.CB_AFTER_SHOT)
        rgb = rawCapture.array
        img = pygame.image.frombuffer(rgb, (self.w, self.h), 'RGB')
        pygame.image.save(img, filename)
        return img

class FakeCamera(Camera):
    def __init__(self):
        Logger.log_warning("Use fake Camera")
        self.resolution = (0, 0)
        self.w = Config.get("snapshot")["w"]
        self.h = Config.get("snapshot")["h"]

    def start(self):
        pass

    def stop(self):
        pass

    def start_preview(self):
        pass

    def stop_preview(self):
        pass

    def set_resolution(self, res):
        self.resolution = res

    def add_overlay(self, overlay_img):
        pass

    def snapshot(self, filename, callbacks):
        self._callback(callbacks, Camera.CB_BEFORE_SHOT)
        time.sleep(2)
        self._callback(callbacks, Camera.CB_AFTER_SHOT)
        time.sleep(1)
        self.resolution = (self.w, self.h)
        img = pygame.image.load("tests/sample_capture.png")
        img = pygame.transform.scale(img, self.resolution)
        pygame.image.save(img, filename)
        return img

