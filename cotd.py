import win32ui, win32gui, win32con, win32api
import numpy as np
import cv2 as cv
import threading
from enum import Enum
from time import sleep

class _Algorithm(Enum):
    default = 0
    gray_diff = 1
    value_diffv1 = 2
    value_diffv2 = 3

class _State(Enum):
    load_bait = 0
    waiting = 1
    fishing = 2


class _CircleDetector: #implement Strategy pattern for free algo swapping!
    def __init__(self, algo=0, pdown=False):
        self._algo = _Algorithm(algo)
        self._callback = None
        self._pdown = pdown
        self._bg_img = cv.imread("./res/background.jpg")

        if self._pdown:
            self._bg_img = cv.pyrDown(self._bg_img)

        if self._algo.value == 1:
            self._bg_img = cv.cvtColor(self._bg_img, cv.COLOR_BGR2GRAY)
        elif self._algo.value == 2:
            self._bg_img = cv.cvtColor(self._bg_img, cv.COLOR_BGR2HSV)
            self._bg_img = self._bg_img[:,:,2]

        if 0 <= self._algo.value <= 2:
            self._callback = self._houghcircles_based
        elif self._algo.value == 3:
            self._callback = self._brightest_region

    def draw_circle(self, img=None, xyr=None, conversion=None):
        canvas = None
        if conversion is not None:
            canvas = cv.cvtColor(img, conversion)
        else:
            canvas = img
            
        if xyr is not None:
            x = xyr[0]
            y = xyr[1]
            r = xyr[2]
            cv.circle(canvas, (x, y), r, (0, 0, 255), 2)

        return canvas

    def _brightest_region(self, img, bg, algo):
        print("not implemented yet")
        return None, None

    def hough(self, img):
        i_mat = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        detected_circles = cv.HoughCircles(
                i_mat, 
                cv.HOUGH_GRADIENT,
                1.2, 20, 
                param1 = 50, 
                param2 = 30, 
                minRadius = 35, 
                maxRadius = 39)
        
        xyr = [0] * 3
        
        if detected_circles is not None: 
            detected_circles = np.uint16(np.around(detected_circles)) 
            for pt in detected_circles[0, :]:
                if self._pdown:
                    xyr[0] = pt[0] * 2
                    xyr[1] = pt[1] * 2
                    xyr[2] = pt[2] * 2
                else:
                    xyr = pt

        return i_mat, xyr, detected_circles

    def _houghcircles_based(self, img, bg, algo):
        if self._pdown:
            img = cv.pyrDown(img)

        i_mat = None
        if algo == _Algorithm.default:
            i_mat = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        elif algo == _Algorithm.gray_diff:
            i_mat = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            i_mat = cv.absdiff(self._bg_img, i_mat)
        elif algo == _Algorithm.value_diffv1:
            fg_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
            i_mat = fg_hsv[:,:,2]
            i_mat = cv.absdiff(self._bg_img, i_mat)

        detected_circles = None

        if self._pdown:
            detected_circles = cv.HoughCircles(
                i_mat, 
                cv.HOUGH_GRADIENT,
                1.6, 20, 
                param1 = 50, 
                param2 = 30, 
                minRadius = 34, 
                maxRadius = 36)
        else:
            detected_circles = cv.HoughCircles(
                i_mat, 
                cv.HOUGH_GRADIENT,
                1.2, 20, 
                param1 = 50, 
                param2 = 30, 
                minRadius = 68, 
                maxRadius = 72)
        
        canvas = cv.cvtColor(i_mat, cv.COLOR_GRAY2BGR)
        
        xyr = [0] * 3
        
        if detected_circles is not None: 
            detected_circles = np.uint16(np.around(detected_circles)) 
            for pt in detected_circles[0, :]:
                if self._pdown:
                    xyr[0] = pt[0] * 2
                    xyr[1] = pt[1] * 2
                    xyr[2] = pt[2] * 2
                else:
                    xyr = pt

        return i_mat, xyr, detected_circles
    
    def get_xyr(self, img=None):
        return self._callback(img, self._bg_img, self._algo)

class _Window:
    def __init__(self, winname="BlueStacks"):
        self._hwnd = win32gui.FindWindow(None, winname)
        self.fix_wpos()
        rect = win32gui.GetWindowRect(self._hwnd)
        self.x1 = rect[0]
        self.y1 = rect[1]
        self.x2 = rect[2]
        self.y2 = rect[3]
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1

    def click(self, x,y):
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        sleep(0.01)

    def fix_wpos(self, width=1099, height=625):
        win32gui.MoveWindow(self._hwnd, 0, 0, width, height, True)

    def screenshot(self, x=0, y=0, w=None, h=None, bmpfilename=None):
        if w is None:
            w = self.width
        if h is None:
            h = self.height
        
        hwnd = self._hwnd
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0,0), (w, h) , dcObj, (x,y), win32con.SRCCOPY)

        if bmpfilename is not None:
            dataBitMap.SaveBitmapFile(cDC, bmpfilename)

        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (h,w,4) #bgra
        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        return cv.cvtColor(img, cv.COLOR_BGRA2BGR)

class CatchOfTheDay:
    def __init__(self, debug=False, fps=10, algo=2):
        self._debug = debug
        self._fps = fps
        self._lock = threading.Event()
        self._cd = _CircleDetector(algo)
        self._state = _State.load_bait

    def start(self):
        bstacks = _Window()
        bstacks.fix_wpos()

        x_catch_area = 500
        y_catch_area = 130

        x_frod_area = 230
        y_frod_area = 532


        while True:
            if self._state == _State.load_bait:
                frame = bstacks.screenshot(x_catch_area, y_catch_area, 475, 350)
                _, coords, detection = self._cd.get_xyr(frame)
                if detection is not None:
                    bstacks.click(132, 588)
                    bstacks.click(coords[0] + x_catch_area, coords[1] + y_catch_area)
                    self._state = _State.waiting

            elif self._state == _State.waiting:
                frame = bstacks.screenshot(x_frod_area, y_frod_area, 74, 74)
                _, coords, detection = self._cd.hough(frame)
                if detection is not None:
                    self._state = _State.fishing
            
            elif self._state == _State.fishing:
                frame = bstacks.screenshot(x_catch_area, y_catch_area, 475, 350)
                _, coords, detection = self._cd.get_xyr(frame)
                if detection is not None:
                    bstacks.click(coords[0] + x_catch_area, coords[1] + y_catch_area)
                frame = bstacks.screenshot(x_frod_area, y_frod_area, 74, 74)
                _, coords, detection = self._cd.hough(frame)
                if detection is not None:
                    self._state = _State.load_bait


                """ if self._debug:
                    img = self._cd.draw_circle(frame, coords, None)
                    cv.imshow("Debug", img)
                    if cv.waitKey(1) & 0xFF == ord('q'):
                        break """
            self._lock.wait(1 / self._fps)