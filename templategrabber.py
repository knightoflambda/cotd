import cv2 as cv
import argparse
import cotd

from windowwrapper import Window

if __name__ == "__main__":
    bstacks = Window("BlueStacks")
    for i in range(4):
        x, y = cotd.FIRST_BAIT_APOS
        x = x + (i * 64) + (i * 10)
        frame = bstacks.screenshot2mat((x, y), (64, 30))
        cv.imwrite("./res/bait{}.jpg".format(i), frame)