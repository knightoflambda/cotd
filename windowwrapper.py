import win32ui, win32gui, win32con, win32api
import numpy as np
from cv2 import cvtColor
from cv2 import COLOR_BGRA2BGR
from time import sleep

class WindowNotFoundException(Exception):
    def __init__(self, winname, message="Window name '{}' not found"):
        self.winname = winname
        self.message = message.format(winname)
        super().__init__(self.message)

class InvalidWindowCoordinatesException(Exception):
    def __init__(self, message="Invalid coordinates given"):
        super().__init__(message)


class Window:
    def __init__(self, winname="BlueStacks"):
        self._hwnd = win32gui.FindWindow(None, winname)
        if self._hwnd == 0:
            raise WindowNotFoundException(winname)
        #self.fix_wpos() #might be redundant
        rect = win32gui.GetWindowRect(self._hwnd)
        self.x1 = rect[0]
        self.y1 = rect[1]
        self.x2 = rect[2]
        self.y2 = rect[3]
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
    
    def click(self, points_offset: tuple, points=(0, 0)):
        if not points_offset:
            raise InvalidWindowCoordinatesException()
        xo, yo = points_offset
        x, y = points
        x = x + xo
        y = y + yo
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        sleep(0.01)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        sleep(0.01)

    def fix_wpos(self, width=1099, height=625):
        win32gui.MoveWindow(self._hwnd, 0, 0, width, height, True)

    def screenshot2mat(self, points: tuple, dims=(), bmpfilename=None):
        x, y = points
        w, h = dims
        if not dims:
            w, h = self.width, self.height
            
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

        return cvtColor(img, COLOR_BGRA2BGR)