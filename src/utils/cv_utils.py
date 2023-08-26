import cv2
import numpy as np
# from pseyepy import cam_count
from PyQt5.QtWidgets import QMessageBox


def check_if_cams_available(is_pseye):
    return False if len(list_of_cams(is_pseye)) <= 0 else True


def show_cam_not_found_warn(parent):
    QMessageBox.warning(parent, 'Предупреждение!',
                        'Не найдены доступные камеры.\nПопробуйте переподключить камеры или обновить их драйвера!')


def list_of_cams(is_pseye=False):
    # if is_pseye:
        # return list(range(cam_count()))

    idx = 0
    res = []
    tries = 3
    while True:
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            if tries >= 0:
                tries -= 1
                continue
            else:
                break

        res.append(idx)
        cap.release()
        idx += 1

    return res


def apply_brightness(input_img, brightness=0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    return buf

def apply_contrast(input_img, contrast=0):
    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)
        input_img = cv2.addWeighted(input_img, alpha_c, input_img, 0, gamma_c)

    return input_img


def apply_saturation(img, vibrance=0):
    imghsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype("float32")
    (h, s, v) = cv2.split(imghsv)
    s = s * vibrance
    s = np.clip(s, 0, 255)
    imghsv = cv2.merge([h, s, v])
    return cv2.cvtColor(imghsv.astype("uint8"), cv2.COLOR_HSV2BGR)


def apply_zoom(frame, zoom=1, interpolation=cv2.INTER_LINEAR):
    cy, cx = [i/2 for i in frame.shape[:-1]]
    rot_mat = cv2.getRotationMatrix2D((cx, cy), 0, zoom)
    return cv2.warpAffine(frame, rot_mat, frame.shape[1::-1], flags=interpolation)
