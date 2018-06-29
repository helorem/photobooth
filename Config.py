import os
import json

class Strings:
    def __init__(self):
        self.data = {}

    def load(self, filename):
        if not os.path.isfile(filename):
            if not self.data:
                Logger.log_error("Cannot open config file '%s'" % filename)
            else:
                Logger.log_warning("Cannot open config file '%s'" % filename)
        else:
            self.data["other_config"] = None
            with open(filename, "r") as fd:
                new_data = json.load(fd)
                for key in new_data:
                    self.data[key] = new_data[key]
            if self.data["other_config"]:
                load(self.data["other_config"])

    def get_val(self, key):
        res = key
        if key in self.data:
            res = self.data[key]
        return res

    @staticmethod
    def get(key):
        return Strings.get_instance().get_val(key)

    _instance = None
    @staticmethod
    def get_instance():
        if not Strings._instance:
            Strings._instance = Strings()
        return Strings._instance


class Config:
    def __init__(self):
        self.data = {}

    def load(self, config_file):
        if not os.path.isfile(config_file):
            Logger.log_error("Cannot open config file '%s'" % config_file)
        else:
            with open(config_file, "r") as fd:
                self.data = json.load(fd)

            folder = Config.get("resources_folder")
            if folder:
                path = os.path.join(folder, "config.json")
                if os.path.isfile(path):
                    with open(path, "r") as fd:
                        self.data.update(json.load(fd))

    def get_val(self, key, default=None):
        res = default
        if key in self.data:
            res = self.data[key]
        return res

    @staticmethod
    def get(key, default=None):
        return Config.get_instance().get_val(key, default)

    _instance = None
    @staticmethod
    def get_instance():
        if not Config._instance:
            Config._instance = Config()
        return Config._instance


