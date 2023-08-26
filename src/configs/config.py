import json
from os import path

def get_path(file):
    return path.abspath(path.join(path.dirname(__file__), file))

class Config:
    instance = None

    @staticmethod
    def get_instance(*args, **kwargs):
        if not Config.instance:
            Config.instance = Config(*args, **kwargs)

        return Config.instance

    def __init__(self, file_path='config.json', default_file_path='config_default.json'):
        self.file_path = get_path(file_path)
        self.default_file_path = get_path(default_file_path)
        self.data = {}
        self.load()

    def get(self, key):
        val = None
        try:
            val = self.data[key]
        except KeyError:
            pass
        return val

    def set(self, key, value):
        self.data[key] = value

    def load(self):
        with open(self.file_path, 'r') as f:
            self.data = json.load(f)

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)

    def set_default(self):
        with open(self.default_file_path, 'r') as default:
            self.data = json.load(default)
            self.save()
