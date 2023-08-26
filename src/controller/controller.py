from pynput import keyboard
from ..configs import Config
from ..start_tracker import Tracker


class Controller:
    def __init__(self, tr: Tracker):
        self.config = Config.get_instance()
        self.tr = tr
        self.x_key = 'offset_x'
        self.y_key = 'offset_y'
        self.init_listeners()

    def init_listeners(self):
        self.listener = keyboard.Listener(
            on_release=self.on_click,
            on_press=self.on_press,
        )
        self.listener.start()

    def on_click(self, key):
        try:
            if (key == keyboard.Key.left or
                    key == keyboard.Key.right or
                    key == keyboard.Key.up or
                    key == keyboard.Key.down):
                self.config.save()

            if key.char == 's':
                self.tr.toggle()
        except AttributeError:
            pass

    def on_press(self, key):
        if key == keyboard.Key.left:
            self.config.set(self.x_key, self.config.get(self.x_key) - 1)
        elif key == keyboard.Key.right:
            self.config.set(self.x_key, self.config.get(self.x_key) + 1)
        elif key == keyboard.Key.up:
            self.config.set(self.y_key, self.config.get(self.y_key) - 1)
        elif key == keyboard.Key.down:
            self.config.set(self.y_key, self.config.get(self.y_key) + 1)
