import time
import photobooth
import pygame
import io

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

    def stop(self):
        if self.camera:
            self.camera.close()

    def set_resolution(self, res):
        self.camera.resolution = res

    def capture_preview(self, stream):
        self.camera.capture(stream, use_video_port=True, format='yuv')

    def _callback(self, callbacks, event):
        if event in callbacks:
            callbacks[event]()

    def snapshot(self, filename, callbacks):
        yuv = bytearray(self.w * self.h * 3 / 2)
        rgb = bytearray(self.w * self.h * 3)
        self.camera.resolution = (self.w, self.h)
        with io.BytesIO() as stream:
            self._callback(callbacks, Camera.CB_BEFORE_SHOT)
            self.camera.capture(stream, format='yuv')
            self._callback(callbacks, Camera.CB_AFTER_SHOT)
            stream.seek(0)
            stream.readinto(yuv)
        photobooth.yuv2rgb(yuv, rgb, self.w, self.h)
        img = pygame.image.frombuffer(rgb[0:(self.w * self.h * 3)], (self.w, self.h), 'RGB')
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

    def set_resolution(self, res):
        self.resolution = res

    def capture_preview(self, stream):
        with open("tests/sample_capture_640_480.yuv", "rb") as fd:
            stream.write(fd.read())

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

