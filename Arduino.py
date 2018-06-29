import threading
import os
import time
import pygame
import traceback

from Logger import Logger
from Config import Config

class Arduino:
    BUTTON_1 = "B1"
    BUTTON_2 = "B2"
    BUTTON_3 = "B3"

    _instance = None
    def __init__(self):
        import serial
        self.serial = None
        self.callbacks = {}
        self.thread = None
        self.looping = False
        self.mutex = threading.Lock()

        serial_name = Config.get("serial_name")
        if not serial_name:
            Logger.log_error("No serial name")
        else:
            serial_wait = Config.get("serial_wait")

            Logger.log_info("Test serial '%s'..." % serial_name)
            found = False
            for i in xrange(1, serial_wait):
                if os.path.exists(serial_name):
                    found = True
                    break
                time.sleep(1)

            if not found:
                Logger.log_error("Serial '%s' not found" % serial_name)
            else:
                Logger.log_info("Serial '%s' found" % serial_name)
                self.serial = serial.Serial(serial_name, baudrate=9600, timeout=2)

        self.flash_off()

    @staticmethod
    def get_instance():
        if not Arduino._instance:
            Arduino._instance = Arduino()
        return Arduino._instance

    def register_callback(self, key, callback, duration=0):
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append((callback, duration))

    def start(self):
        self.thread = threading.Thread(None, self._loop)
        self.thread.start()

    def stop(self):
        self.looping = False
        self.thread.join(5)

    def _loop(self):
        self.looping = True

        while self.looping:
            try:
                self.mutex.acquire()
                cmd = self.serial.readline()
                self.mutex.release()
                if cmd:
                    cmd = cmd.strip()
                    Logger.log_debug("Button : %s" % cmd)
                    if cmd in self.callbacks:
                        for callback, duration in self.callbacks[cmd]:
                            if callback():
                                break
                time.sleep(0.1)
            except Exception as ex:
                Logger.log_warning("Button read : %s" % str(ex))
                Logger.log_debug(traceback.format_exc())

    def close(self):
        if self.serial:
            self.serial.close()

    def write(self, txt):
        if self.serial:
            self.mutex.acquire()
            self.serial.write(txt)
            self.mutex.release()

    def flash_on(self):
        self.write("SF116\n")
        self.write("SF216\n")

    def flash_off(self):
        self.write("SF100\n")
        self.write("SF200\n")

    def shutdown(self):
        for i in xrange(5):
            self.write("SB116\n")
            self.write("SB216\n")
            time.sleep(0.25)
            self.write("SB100\n")
            self.write("SB200\n")
            time.sleep(0.25)

class FakeArduino(Arduino):
    MATCHING = {
        pygame.K_e : Arduino.BUTTON_1,
        pygame.K_a : Arduino.BUTTON_2,
        pygame.K_z : Arduino.BUTTON_3
    }

    def __init__(self):
        Logger.log_warning("Use fake Arduino ('A' = BTN1, 'E' = BTN2, 'Z' = BTN3)")
        self.callbacks = {}
        self.thread = None
        self.looping = False

    def register_callback(self, key, callback, duration=0):
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append((callback, duration))

    def start(self):
        self.thread = threading.Thread(None, self._loop)
        self.thread.start()

    def stop(self):
        self.looping = False
        self.thread.join(5)

    def _loop(self):
        self.looping = True

        cmd_duration = ["", 0]
        while self.looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.callbacks[Arduino.BUTTON_3][0][0]()
                elif event.type == pygame.KEYDOWN and event.key in FakeArduino.MATCHING:
                    cmd = FakeArduino.MATCHING[event.key]
                    if cmd != cmd_duration[0]:
                        cmd_duration = [cmd, time.time()]

                    Logger.log_debug("Button : %s" % cmd)
                    if cmd in self.callbacks:
                        for callback, duration in self.callbacks[cmd]:
                            cmd_dur = int(time.time() - cmd_duration[1])
                            if cmd_dur == duration:
                                if callback():
                                    cmd_duration = ["", 0]
                                    break

    def close(self):
        pass

    def flash_on(self):
        Logger.log_debug("Flash ON")

    def flash_off(self):
        Logger.log_debug("Flash OFF")

    def shutdown(self):
        pass

    @staticmethod
    def get_instance():
        if not Arduino._instance:
            Arduino._instance = FakeArduino()
        return Arduino._instance


