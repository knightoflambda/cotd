import argparse
import threading
import imageprocessor
import logging

from windowwrapper import Window
from enum import Enum
from time import sleep
from time import time

VERSION = "LATTE (v0.31)"
FIRST_BAIT_APOS = (132, 588)

CATCH_AREA_POINTS = 500, 130
CATCH_AREA_DIMS = 475, 350

FROD_AREA_POINTS = 230, 532
FROD_AREA_DIMS = 74, 74

class State(Enum):
    load_bait = 0
    waiting = 1
    fishing = 2

if __name__ == "__main__":
    fmt_str = '[%(asctime)s] %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt_str, datefmt='%H:%M:%S')
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fps", 
        help="set program refresh rate for screencapture", type=int, default=10)
    parser.add_argument("-d", "--debug",
        help="turns on debug mode", action="store_true")
    parser.add_argument("-v", "--verbose",
        help="shows state and compute time of \
                compute-intensive functions", type=int, default=1)
    parser.add_argument("-a", "--algorithm",
        help="sets the primary algorithm for circle detection", type=int, default=1)
    args = parser.parse_args()

    print("\nPetPals - Catch of the Day")
    print("Author: l4mbda")
    print("Program Version: %s" % VERSION)
    print("\nJob 1:21\tthe LORD gave, and the LORD hath taken away;\n\t\tblessed be the name of the LORD\n")
    print("\nPsalm 115:1\tNot unto us, O Lord, not unto us, \n\t\tbut unto thy name give glory,\n\t\tfor thy mercy, and for thy truth's sake.\n")
    print("\nJames 1:17\tEvery good and perfect gift is from above,\n\t\tcoming down from the Father of the heavenly lights\n")

    if args.verbose == 1:
        print("Running with params: ")
        print("\tFPS: %d" % args.fps)
        print("\tDebug Mode: %s" % args.debug)
        print("\tVerbose Level: %d" % args.verbose)
        print("\tAlgorithm: %d" % args.algorithm)
    
    print()
    
    
    # initialize tools
    bstacks = Window("BlueStacks")
    bg_path = "./res/background.jpg"
    frod_path = "./res/frod_pos.jpg"

    catch_detect_algo = None
    if args.algorithm == 0:
        catch_detect_algo = imageprocessor.DefaultHough(imageprocessor.CATCH_CIRCLE_R)
    elif args.algorithm == 1:
        catch_detect_algo = imageprocessor.GrayDiff(bg_path, imageprocessor.CATCH_CIRCLE_R)
    elif args.algorithm == 2:
        catch_detect_algo = imageprocessor.ValueDiff1(bg_path, imageprocessor.CATCH_CIRCLE_R)
    
    frod_algo = imageprocessor.TemplateMatch(frod_path)
    frod_detector = imageprocessor.ObjectDetector(frod_algo)
    catch_detector = imageprocessor.ObjectDetector(catch_detect_algo)

    # initialize variables
    prev_state = None
    state = State.load_bait
    time_ref = time()

    """ import numpy as np
    test_img = np.zeros(shape=(72,72,3)).astype('uint8')
    cv2.imshow('debug',test_img)
    cv2.moveWindow('debug',1720,600)
    cv2.waitKey(1)  """

    while True:
        if args.verbose == 1:
            if prev_state != state:
                logger.info(str(state))
            prev_state = state
            
        if state == State.load_bait:
            frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
            catch = catch_detector.get_detected_coords(frame)
            if catch:
                bstacks.click(FIRST_BAIT_APOS)
                x, y, r = catch
                bstacks.click(CATCH_AREA_POINTS, (x,y))
                state = State.waiting
        elif state == State.waiting:
            if (time() - time_ref) > 11:
                if args.verbose == 1:
                    logger.info("Deadlocked in wait, resetting state...")
                time_ref = time()
                state = State.load_bait

            frame = bstacks.screenshot2mat(FROD_AREA_POINTS, FROD_AREA_DIMS)
            frod = frod_detector.get_detected_coords(frame)
            if frod:
                state = State.fishing
        elif state == State.fishing:
            fframe = bstacks.screenshot2mat(FROD_AREA_POINTS, FROD_AREA_DIMS)
            frod = frod_detector.get_detected_coords(fframe)
            if not frod:
                state = State.load_bait
            else:
                cframe = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
                catch = catch_detector.get_detected_coords(cframe)
                if catch:
                    x, y, r = catch
                    bstacks.click(CATCH_AREA_POINTS, (x, y))
        
        time_ref = time()
        """ if args.debug:
            frame = bstacks.screenshot2mat(FROD_AREA_X, FROD_AREA_Y, 74, 74)
            frod = frod_detector.get_detected_coords(frame)
            if frod:
                frame = frod_detector.draw_circle(frame, frod)
            imshow("debug", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break """

        sleep(1/args.fps)