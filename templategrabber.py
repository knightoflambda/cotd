import cv2 as cv
import argparse
AREA_POINTS = 790, 130
AREA_DIMS = 185, 43
from windowwrapper import Window

if __name__ == "__main__":
    bstacks = Window("BlueStacks")
    bstacks.fix_wpos()
    x, y = AREA_POINTS
    w, h = AREA_DIMS

    frame = bstacks.screenshot2mat((x, y), (w, h))
    cv.imwrite("./res/half_moon.jpg", frame)
