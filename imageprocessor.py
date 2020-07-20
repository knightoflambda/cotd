import cv2 as cv
import numpy as np

CATCH_CIRCLE_R = (68, 72)
FROD_CIRCLE_R = (34, 36)

class Canvas:
    def __init__(self):
        self._display = None

class ObjectDetectionAlgorithm:

    def get_coords(self, rmat) -> tuple:
        pass

    def template_match(self, template, imat, thresh, tm_algo=cv.TM_CCOEFF_NORMED):
        xy = ()
        res = cv.matchTemplate(imat, template, tm_algo)
        if res >= thresh:
            if len(imat.shape) == 3:
                w, h, _ = imat.shape
            elif len(imat.shape) == 2:
                w, h = imat.shape
            xy = (round(w/2), round(h/2))
        return xy

    def detected_circles(self, imat, dp, mind, p1, p2, minr, maxr, ipyr=0):
        xyr = ()
        if imat is not None:
            circles = cv.HoughCircles(imat, cv.HOUGH_GRADIENT, dp, mind,
                                    None, p1, p2, minr, maxr)
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    x = x * (ipyr + 1)
                    y = y * (ipyr + 1)
                    r = r * (ipyr + 1)
                    xyr = (x, y, r)

        return xyr


class DefaultHough(ObjectDetectionAlgorithm):
    def __init__(self, minmaxr: tuple, dp=1.2, p1=50, p2=30, ipyr=0):
        self._dp = dp
        self._p1 = p1
        self._p2 = p2
        self._minr, self._maxr = minmaxr
        self._ipyr = ipyr
        self._mind = 1000


    def get_coords(self, rmat=None) -> tuple:
        imat = None
        xyr = ()
        if rmat is not None:
            _, _, c = rmat.shape
            if c == 1:
                imat = rmat
            elif c == 3:
                imat = cv.cvtColor(rmat, cv.COLOR_BGR2GRAY)
            
            xyr = super().detected_circles(imat, self._dp, self._mind, 
                                            self._p1, self._p2, self._minr, 
                                            self._maxr, self._ipyr)
        
        return xyr
            
class GrayDiff(ObjectDetectionAlgorithm):
    def __init__(self, bg_ref: str, minmaxr: tuple, dp=1.2, p1=50, p2=30, ipyr=0):
        self._dp = dp
        self._p1 = p1
        self._p2 = p2
        self._minr, self._maxr = minmaxr
        self._ipyr = ipyr
        self._mind = 1000
        
        ref = cv.imread(bg_ref)
        self._bg_ref = cv.cvtColor(ref, cv.COLOR_BGR2GRAY)


    def get_coords(self, rmat=None) -> tuple:
        imat = None
        xyr = ()
        if rmat is not None:
            _, _, c = rmat.shape
            if c == 1:
                imat = rmat
            elif c == 3:
                imat = cv.cvtColor(rmat, cv.COLOR_BGR2GRAY)
            
            imat = cv.absdiff(self._bg_ref, imat)
            xyr = super().detected_circles(imat, self._dp, self._mind, 
                                            self._p1, self._p2, self._minr, 
                                            self._maxr, self._ipyr)
        return xyr

class ValueDiff1(ObjectDetectionAlgorithm):
    def __init__(self, bg_ref: str, minmaxr: tuple, dp=1.2, p1=50, p2=30, ipyr=0):
        self._dp = dp
        self._p1 = p1
        self._p2 = p2
        self._minr, self._maxr = minmaxr
        self._ipyr = ipyr
        self._mind = 1000

        ref = cv.imread(bg_ref)
        self._bg_ref = cv.cvtColor(ref, cv.COLOR_BGR2HSV)


    def get_coords(self, rmat=None) -> tuple:
        imat = None
        xyr = ()
        if rmat is not None:
            _, _, c = rmat.shape
            if c == 1:
                imat = rmat
            elif c == 3:
                imat = cv.cvtColor(rmat, cv.COLOR_BGR2HSV)

            imat = cv.absdiff(self._bg_ref[:, :, 2], imat[:, :, 2])
            xyr = super().detected_circles(imat, self._dp, self._mind, 
                                            self._p1, self._p2, self._minr, 
                                            self._maxr, self._ipyr)
        return xyr

class ValueDiff2(ObjectDetectionAlgorithm):
    def get_coords(self, rmat) -> tuple:
        pass

class TemplateMatch(ObjectDetectionAlgorithm):
    def __init__(self, bg_ref, gray=True, thresh=0.8):
        self._bg_ref = None
        self._gray = gray
        self._thresh = thresh
        if gray:
            self._bg_ref = cv.imread(bg_ref, 0)
        else:
            self._bg_ref = cv.imread(bg_ref)

    def get_coords(self, rmat) -> tuple:
        xy = ()
        if self._gray: 
            imat = cv.cvtColor(rmat, cv.COLOR_BGR2GRAY)
        else:
            imat = rmat
        xy = super().template_match(self._bg_ref, imat, self._thresh)
        return xy


class ObjectDetector:
    def __init__(self, algorithm: ObjectDetectionAlgorithm):
        self._algorithm = algorithm
    
    def get_detected_coords(self, rmat) -> tuple:
        return self.algorithm.get_coords(rmat)

    @property
    def algorithm(self) -> ObjectDetectionAlgorithm:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm: ObjectDetectionAlgorithm) -> None:
        self._algorithm = algorithm

    def draw_circle(self, img=None, xyr=(), conversion=None):
        canvas = None
        if conversion is not None:
            canvas = cv.cvtColor(img, conversion)
        else:
            canvas = img
            
        if xyr:
            x, y, r = xyr
            cv.circle(canvas, (x, y), r, (0, 0, 255), 2)

        return canvas