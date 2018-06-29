import os

from Config import Config

class ResourceManager:
    _instance = None

    def __init__(self):
        self.folders = ["assets"]

        self.add_folder(Config.get("resources_folder"))

    def add_folder(self, folder):
        if folder and folder not in self.folders:
            self.folders.insert(0, folder)

    def get_folder(self):
        for folder in self.folders:
            if os.path.exists(folder):
                return folder
        return "."


    def get_val(self, filename):
        for folder in self.folders:
            path = os.path.join(folder, filename)
            print "resourcemanager : %s" % path
            if os.path.isfile(path):
                return path
        return None

    @staticmethod
    def get(filename):
        return ResourceManager.get_instance().get_val(filename)

    @staticmethod
    def get_instance():
        if not ResourceManager._instance:
            ResourceManager._instance = ResourceManager()
        return ResourceManager._instance


