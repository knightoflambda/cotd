import cv2 as cv
import numpy as np

CATCH_CIRCLE_R = (68, 72)
FROD_CIRCLE_R = (34, 36)

class InvalidImagePathException(Exception):
    def __init__(self, path, message="Invalid image path '%s' given"):
        self.message = message.format(path)
        super().__init__(self.message)

class MinMaxRadiusException(Exception):
    def __init__(self, message="Min and max radius not specified"):
        super().__init__(message)


class ObjectLocator:
    def find_object(self, img) -> tuple: pass # tuple containing at least object coordinates and a mat object


class TemplateMatchLocator(ObjectLocator):
    def __init__(self, path_thresh: list):
        self._temp_thresh = []

        for pt in path_thresh:
            path, thresh = pt
            mat = cv.imread(path)
            if mat is None:
                raise InvalidImagePathException()
            else:
                self._temp_thresh.append((mat, thresh))

    def find_object(self, img):
        mat = img
        xy = ()
        res = 0
        for template_thresh in self._temp_thresh:
            template, thresh = template_thresh
            res = cv.matchTemplate(mat, template, cv.TM_CCOEFF_NORMED)
            if res >= thresh:
                w, h, _ = mat.shape
                xy = (round(w/2), round(h/2))

        return (xy, res * 100, mat)


class CircleLocator(ObjectLocator):
    def __init__(self, temp_path):
        mat = cv.imread(temp_path)
        self._template = None
        if mat is None:
            raise InvalidImagePathException()
        else:
            hsv = cv.cvtColor(mat, cv.COLOR_BGR2HSV)
            self._template = hsv[:, :, 2]


    def find_object(self, img, minmaxr=()):
        xyr = ()
        if not minmaxr:
            raise MinMaxRadiusException()
        minr, maxr = minmaxr
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        img_v = hsv[:, :, 2]
        imat = cv.absdiff(self._template, img_v)
        circles = cv.HoughCircles(imat, cv.HOUGH_GRADIENT, 1.2, 1000, None, 50, 30, minr, maxr)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                """ x = x * (ipyr + 1)
                y = y * (ipyr + 1)
                r = r * (ipyr + 1) """
                xyr = (x, y, r)


        return (xyr, imat)


class Canvas:
    def __init__(self):
        self._display = None