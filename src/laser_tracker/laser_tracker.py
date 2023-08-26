import cv2
from ..configs import Config


class LaserTracker(object):
    def __init__(self):
        self.config = Config.get_instance()
        self.capture = None
        self.channels = {
            'hue': None,
            'saturation': None,
            'value': None,
            'laser': None,
        }

    def threshold_image(self, channel):
        key = "hue" if channel == "hue" else "sat" if channel == "saturation" else "val"
        minimum = self.config.get(key + '_min')
        maximum = self.config.get(key + '_max')

        (t, tmp) = cv2.threshold(
            self.channels[channel],  # src
            maximum,  # threshold value
            0,  # we dont care because of the selected type
            cv2.THRESH_TOZERO_INV  # t type
        )

        (t, self.channels[channel]) = cv2.threshold(
            tmp,  # src
            minimum,  # threshold value
            255,  # maxvalue
            cv2.THRESH_BINARY  # type
        )

        if channel == 'hue':
            # only works for filtering red color because the range for the hue
            # is split
            self.channels['hue'] = cv2.bitwise_not(self.channels['hue'])

    def track(self, frame, mask):
        countours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        # only proceed if at least one contour was found
        if len(countours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(countours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            moments = cv2.moments(c)
            if moments["m00"] > 0:
                center = [int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"])]
            else:
                center = [x, y]

            offset_x = self.config.get('offset_x')
            offset_y = self.config.get('offset_y')

            center[0] += offset_x
            center[1] += offset_y

            x += offset_x
            y += offset_y

            # only proceed if the radius meets a minimum size
            if self.config.get("min_dot_rad") < radius < self.config.get("max_dot_rad"):
                # draw the circle and centroid on the frame,
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, (int(center[0]), int(center[1])), 5, (0, 0, 255), -1)

                return center, radius
            return None, radius

    def detect(self, frame):
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # split the video frame into color channels
        h, s, v = cv2.split(hsv_img)

        self.channels['hue'] = h
        self.channels['saturation'] = s
        self.channels['value'] = v

        # Threshold ranges of HSV components; storing the results in place
        self.threshold_image("hue")
        self.threshold_image("saturation")
        self.threshold_image("value")

        # Perform an AND on HSV components to identify the laser!
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['hue'],
            self.channels['value']
        )

        self.channels['laser'] = cv2.bitwise_and(
            self.channels['saturation'],
            self.channels['laser']
        )

        # Merge the HSV components back together.
        hsv_image = cv2.merge([
            self.channels['hue'],
            self.channels['saturation'],
            self.channels['value'],
        ])

        data = self.track(frame, self.channels['laser'])

        return hsv_image, data

    def get_data(self, frame):
        self.channels['hsv'], data = self.detect(frame)

        return data, frame, self.channels
