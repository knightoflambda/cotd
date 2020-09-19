import cv2 as cv
import argparse
import cotd

from windowwrapper import Window

if __name__ == "__main__":
    bstacks = Window("BlueStacks")
    x, y = cotd.FROD_AREA_POINTS
    w, h = cotd.FROD_AREA_DIMS

    frame = bstacks.screenshot2mat((x, y), (w, h))
    cv.imwrite("./res/frod_beach.jpg", frame)
