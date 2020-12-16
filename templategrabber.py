import cv2 as cv
import argparse

CATCH_AREA_POINTS = 500, 130
CATCH_AREA_DIMS = 475, 350
CATCH_AREA_NAME = 'bg_neko2'

FROD_AREA_POINTS = 230, 532
FROD_AREA_DIMS = 74, 74
FROD_NAME = 'frod_neko'

from windowwrapper import Window

def capture(points: tuple, dims: tuple, name: str):
    x, y = points
    w, h = dims
    frame = bstacks.screenshot2mat((x, y), (w, h))
    cv.imwrite("./res/" + name + ".jpg", frame)


if __name__ == "__main__":
    bstacks = Window("BlueStacks")
    bstacks.fix_wpos()
    capture(FROD_AREA_POINTS, FROD_AREA_DIMS, FROD_NAME)

