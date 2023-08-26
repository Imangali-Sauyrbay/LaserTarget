import cv2
from .abs_videcapture import AbstractVideoCapture


class CV2VideoCapture(AbstractVideoCapture):
    def _init(self):
        self.changeResolution.connect(self.set_res)
        self.changeCurrentCamera.connect(self.change_camera)

    def change_camera(self):
        idx = self.config.get('camera')
        if self.cap or (self.cap and idx < 0):
            self.cap.release()
        if idx < 0:
            return

        self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        self.set_res()
        self.update_camera_config()

    def release_capture(self):
        if self.cap:
            self.cap.release()

    def get_frame(self):
        return self.cap.read()

    def set_res(self):
        x, y = self.config.get("selected_resolution").split('x')
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))

    def update_camera_config(self):
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.config.get('camera_brightness'))
            self.cap.set(cv2.CAP_PROP_CONTRAST, self.config.get('camera_contrast'))
            self.cap.set(cv2.CAP_PROP_SATURATION, self.config.get('camera_sat'))
            self.cap.set(cv2.CAP_PROP_HUE, self.config.get('camera_hue'))

    def last_frame_manipulation(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
