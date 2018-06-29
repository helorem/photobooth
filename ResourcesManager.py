import os

class ResourceManager:
    _instance = None

    def __init__(self):
        self.folders = ["./Resources"]

    def add_folder(self, folder):
        self.folders.insert(0, folder)

    def get_val(self, filename):
        for folder in self.folders:
            path = os.path.join(folder, filename)
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


