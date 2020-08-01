import cv2 as cv
import numpy as np

CATCH_CIRCLE_R = (66, 70)
FROD_CIRCLE_R = (34, 36)

class ImageDisplay:
    def __init__(self, winname: str, coords: tuple):
        self._winname = winname
        placeholder_mat = np.zeros(shape=(200,200,3)).astype('uint8')
        cv.imshow(self._winname, placeholder_mat)
        x, y = coords
        cv.moveWindow(winname, x, y)
        cv.waitKey(1)

    def set_image(self, image):
        cv.imshow(self._winname, image)
        cv.waitKey(1)

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

        self._cspace = cv.COLOR_BGR2LAB
        self._channel = 0
        self._template = None

        if mat is None:
            raise InvalidImagePathException()
        else:
            cspace = cv.cvtColor(mat, self._cspace)
            self._template = cspace[:, :, self._channel]


    def find_object(self, img, minmaxr=()):
        xyr = ()
        if not minmaxr:
            raise MinMaxRadiusException()
        minr, maxr = minmaxr
        cspace = cv.cvtColor(img, self._cspace)
        img_v = cspace[:, :, self._channel]
        imat = cv.absdiff(self._template, img_v)
        #imat = cv.blur(imat,(5,5))
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

    def draw_circle(self, img, minmaxr):
        minr, maxr = minmaxr
        circles = cv.HoughCircles(img, cv.HOUGH_GRADIENT, 1.2, 1000, None, 50, 30, minr, maxr)
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
                img = cv.circle(img, (x,y), r, (0, 0, 255), 2)
        
        return img