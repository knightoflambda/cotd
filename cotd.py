import argparse
import threading
import sys
import imageprocessor

from windowwrapper import Window
from enum import Enum
from time import sleep
from time import time

VERSION = "LATTE (v0.30)"
FIRST_BAIT_APOS = (132, 588)

CATCH_AREA_X = 500
CATCH_AREA_Y = 130
CATCH_AREA_W = 475
CATCH_AREA_H = 350

FROD_AREA_X = 230
FROD_AREA_Y = 532

class State(Enum):
    load_bait = 0
    waiting = 1
    fishing = 2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fps", 
        help="set program refresh rate for screencapture", type=int, default=10)
    parser.add_argument("-d", "--debug",
        help="turns on debug mode", type=bool, default=False)
    parser.add_argument("-v", "--verbose",
        help="shows state and compute time of \
                compute-intensive functions", type=int, default=0)
    parser.add_argument("-a", "--algorithm",
        help="sets the primary algorithm for circle detection", type=int, default=1)
    args = parser.parse_args()

    print("PetPals - Catch of the Day")
    print("Author: l4mbda")
    print("Program Version: %s\n" % VERSION)
    print("Job 1:21\tthe LORD gave, and the LORD hath taken away;\n\t\tblessed be the name of the LORD\n")
    print("Psalm 115:1\tNot unto us, O Lord, not unto us, \n\t\tbut unto thy name give glory,\n\t\tfor thy mercy, and for thy truth's sake.\n")
    print("James 1:17\tEvery good and perfect gift is from above,\n\t\tcoming down from the Father of the heavenly lights\n")

    if args.verbose == 1:
        print("Running with params: ")
        print("\tFPS: %d" % args.fps)
        print("\tDebug Mode: %s" % args.debug)
        print("\tVerbose Level: %d" % args.verbose)
        print("\tAlgorithm: %d" % args.algorithm)
    
    # initialize tools
    bstacks = Window("BlueStacks")

    catch_minr, catch_maxr = imageprocessor.CATCH_CIRCLE_R
    bg_path = "./res/background.jpg"
    frod_path = "./res/frod.jpg"

    cda = None
    if args.algorithm == 0:
        cda = imageprocessor.DefaultHough(catch_minr, catch_maxr)
    elif args.algorithm == 1:
        cda = imageprocessor.GrayDiff(bg_path, catch_minr, catch_maxr)
    elif args.algorithm == 2:
        cda = imageprocessor.ValueDiff1(bg_path, catch_minr, catch_maxr)
    
    frod_minr, frod_maxr = imageprocessor.FROD_CIRCLE_R
    fishing_rod = imageprocessor.DefaultHough(frod_minr, frod_maxr)

    frod_detector = imageprocessor.CircleDetector(fishing_rod)
    detector = imageprocessor.CircleDetector(cda)

    # initialize variables
    prev_state = None
    state = State.load_bait
    time_ref = time()

    while True:
        if args.verbose == 1:
            if prev_state != state:
                print("[INFO]: %s" % state)
            prev_state = state
            
        if state == State.load_bait:
            frame = bstacks.screenshot2mat(CATCH_AREA_X, CATCH_AREA_Y, CATCH_AREA_W, CATCH_AREA_H)
            catch = detector.algo_circle_xyr(frame)
            if catch:
                bstacks.click(*FIRST_BAIT_APOS)
                x, y, r = catch
                bstacks.click(x + CATCH_AREA_X, y + CATCH_AREA_Y)
                state = State.waiting
        elif state == State.waiting:
            if (time() - time_ref) > 11:
                if args.verbose == 1:
                    print("[INFO]: Deadlocked in wait, resetting state...")
                time_ref = time()
                state = State.load_bait

            frame = bstacks.screenshot2mat(FROD_AREA_X, FROD_AREA_Y, 74, 74)
            frod = frod_detector.algo_circle_xyr(frame)
            if frod:
                state = State.fishing
        elif state == State.fishing:
            fframe = bstacks.screenshot2mat(FROD_AREA_X, FROD_AREA_Y, 74, 74)
            frod = frod_detector.algo_circle_xyr(fframe)
            if not frod:
                state = State.load_bait
            else:
                cframe = bstacks.screenshot2mat(CATCH_AREA_X, CATCH_AREA_Y, CATCH_AREA_W, CATCH_AREA_H)
                catch = detector.algo_circle_xyr(cframe)
                if catch:
                    x, y, r = catch
                    bstacks.click(x + CATCH_AREA_X, y + CATCH_AREA_Y)
        
        time_ref = time()
        sleep(1/args.fps)