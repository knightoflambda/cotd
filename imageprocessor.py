import cv2 as cv
import numpy as np
from cotd import CATCH_AREA_DIMS

CATCH_CIRCLE_R = (66, 70)
FROD_CIRCLE_R = (34, 36)

class CircleLocator:
    def __init__(self, params: list):
        self._p1 = params[0]
        self._p2 = params[1]
        self._minr = params[2]
        self._maxr = params[3]

    def locate(self, image):
        gray = None
        circle = None
        if len(image.shape) > 2:
            gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        else:
            gray = image
            circle = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1.2, 1000, None, self._p1, self._p2, self._minr, self._maxr)
            if circle is not None:
                circle = np.round(circle[0, 0, :]).astype("int")

        return circle


class CSConverter:
    def __init__(self):
        pass

    def bgr2ihsv(self, image, channel):
        return cv.cvtColor(image, cv.COLOR_BGR2HSV)[:, :, channel]

class ForegroundExtractor:
    def __init__(self, colors: list):
        # test data
        colors = [ # bgr format
            [229, 215, 133],
            [237, 231, 156],
            [244, 241, 180], 
            [255, 253, 241], # +-5
            [254, 247, 214],
            [255, 234, 182],
            [222, 216, 87],
            [167, 146, 64],
            [195, 181, 68],
            # left - up
            [134, 65, 56],
            [224, 208, 201],
            [237, 232, 231],
            [192, 167, 157]
        ]

        self._colors = colors

    def extract(self, image):
        width, height = CATCH_AREA_DIMS
        masks = np.zeros((height,width), np.uint8)
        
        for color in self._colors:
            mask = cv.inRange(image, np.array([x - 3 for x in color]), np.array([x + 3 for x in color]))
            masks = cv.bitwise_or(masks, mask)
        
        image[masks > 0] = (0,0,0)
        
        return image


class TemplateMatcher:
    def __init__(self, template, thresh):
        self._template = cv.imread(template)
        self._thresh = thresh

    def is_match(self, image):
        res = cv.matchTemplate(image, self._template, cv.TM_CCOEFF_NORMED)
        return res >= self._thresh

class Canvas:
    def __init__(self, winname, width, height):
        self._winname = winname
        self._image = np.zeros((height, width, 3), np.uint8)
        cv.imshow(self._winname, self._image)
        cv.moveWindow(self._winname, 0, 650)
        cv.waitKey(1)


    def display(self):
        cv.imshow(self._winname, self._image)
        cv.waitKey(1)

    def store(self, image):
        self._image = image

    def draw_circle(self, xyr):
        x, y, r = xyr
        self._image = cv.circle(self._image, (x, y), r, (0,0,255))