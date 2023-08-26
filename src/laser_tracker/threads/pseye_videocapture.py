# import pseyepy
from .abs_videcapture import AbstractVideoCapture
from ...utils import clamp

class PSEyeVideoCapture(AbstractVideoCapture):
    def _init(self):
        self.changeCurrentCamera.connect(self.change_camera)

    def change_camera(self):
        idx = self.config.get('camera')
        if self.cap or (self.cap and idx < 0):
            self.cap.end()
        if idx < 0:
            return

        # self.cap = pseyepy.Camera(idx, resolution=pseyepy.Camera.RES_LARGE, fps=self.config.get('fps'))
        self.update_camera_config()

    def release_capture(self):
        if self.cap:
            self.cap.end()

    def get_frame(self):
        frame, t = self.cap.read()
        return t, frame

    def last_frame_manipulation(self, frame):
        return frame

    def update_camera_config(self):
        if self.cap is not None:
            self.cap.gain = clamp(self.config.get('pseye_gain'), 0, 63)
            self.cap.exposure = clamp(self.config.get('pseye_exposure'), 0, 255)
            self.cap.red_balance = clamp(self.config.get('red_balance'), 0, 255)
            self.cap.blue_balance = clamp(self.config.get('blue_balance'), 0, 255)
            self.cap.green_balance = clamp(self.config.get('green_balance'), 0, 255)

