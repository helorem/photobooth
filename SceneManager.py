import time
from Logger import Logger

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        self.main_scene = None
        self.looping = False

    def start(self):
        if self.main_scene:
            self.show_main_scene()

        self.looping = True
        while self.looping:
            time.sleep(1)

    def stop(self):
        self.looping = False

    def add_scene(self, scene):
        self.scenes[scene.get_name()] = scene

    def get_scene(self, name):
        res = None
        if name in self.scenes:
            res = self.scenes[name]
        return res

    def show_scene(self, name, params=None):
        if self.current_scene:
            self.current_scene.hide()
        self.current_scene = self.get_scene(name)
        if self.current_scene:
	    Logger.log_debug("Show scene '%s'" % name)
            if params:
                self.current_scene.show(params)
            else:
                self.current_scene.show()

    def show_main_scene(self):
        self.show_scene(self.main_scene)

    def set_main_scene(self, name):
        self.main_scene = name

    _instance = None
    @staticmethod
    def get_instance():
        if not SceneManager._instance:
            SceneManager._instance = SceneManager()
        return SceneManager._instance


