import argparse
import threading
import imageprocessor
import logging
import sys

from windowwrapper import Window
from enum import Enum
from time import sleep
from datetime import datetime

VERSION = "MACCHIATO (v0.5)"
FIRST_BAIT_APOS = (101, 553) #101, 553:65x65 + 11x65

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
    parser.add_argument("-b", "--bait",
        help="sets the baiting method: [first, bait]", type=str, default="first")
    args = parser.parse_args()

    print("\nPetPals - Catch of the Day")
    print("Author: l4mbda")
    print("Program Version: %s" % VERSION)
    print("\nJob 1:21\tthe LORD gave, and the LORD hath taken away;\n\t\tblessed be the name of the LORD\n")
    print("\nPsalm 115:1\tNot unto us, O Lord, not unto us, \n\t\tbut unto thy name give glory,\n\t\tfor thy mercy, and for thy truth's sake.\n")
    print("\nJames 1:17\tEvery good and perfect gift is from above,\n\t\tcoming down from the Father of the heavenly lights\n")

    bait_style = None

    if args.bait == "first":
        bait_style = "Pick first bait only"
    else:
        bait_style = "{} only".format(args.bait)


    if args.verbose == 1:
        print("Running with params: ")
        print("\tFPS: %d" % args.fps)
        print("\tDebug Mode: %s" % args.debug)
        print("\tVerbose Level: %d" % args.verbose)
        print("\tBaiting Style: %s" % bait_style)
    
    print("\n")
    sys.stdout.flush()
    
    # initialize tools
    bstacks = Window("BlueStacks")
    bstacks.fix_wpos()
    catch_region_path = "./res/catch_region.jpg"
    frod_path = "./res/frod_pos.jpg"
    if args.bait != "first":
        bait_path = "./res/{}.jpg".format(args.bait)
    
    bait_coords_center = ()
    if args.bait != "first":
        bait_loc = imageprocessor.TemplateMatchLocator([(bait_path, 0.9)])
    frod_loc = imageprocessor.TemplateMatchLocator([(frod_path, 0.7)])
    catch_loc = imageprocessor.CircleLocator(catch_region_path)

    # initialize variables
    prev_state = None
    state = State.load_bait
    time_ref = None

    while True:
        if args.verbose == 1:
            if prev_state != state:
                logger.info(str(state))
            prev_state = state
            
        if state == State.load_bait:
            time_ref = datetime.now()
            frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
            catch, _ = catch_loc.find_object(frame, imageprocessor.CATCH_CIRCLE_R)
            if catch:
                if args.bait == "first":
                    x, y = FIRST_BAIT_APOS
                    bait_coords_center = (x + 32, y + 32)
                else:
                    for i in range(11):
                        x, y = FIRST_BAIT_APOS
                        x = x + (i * 64) + (i * 10)
                        bait_frame = bstacks.screenshot2mat((x, y), (64, 30))
                        bait_exist, res, _ = bait_loc.find_object(bait_frame)
                        if bait_exist:
                            if args.verbose == 1:
                                logger.info("%s found in index %d, %.2f%% match",args.bait, i, res)
                            bait_coords_center = (x + 32, y + 32)
                            break
                bstacks.click(bait_coords_center)
                x, y, r = catch
                bstacks.click(CATCH_AREA_POINTS, (x,y))
                state = State.waiting
        elif state == State.waiting:
            delta = datetime.now() - time_ref
            seconds = delta.total_seconds()
            if (seconds) > 15:
                if args.verbose == 1:
                    logger.info("Deadlocked in wait, resetting state...")
                state = State.load_bait

            frame = bstacks.screenshot2mat(FROD_AREA_POINTS, FROD_AREA_DIMS)
            frod, _, _ = frod_loc.find_object(frame)
            if frod:
                state = State.fishing

        elif state == State.fishing:
            frod_frame = bstacks.screenshot2mat(FROD_AREA_POINTS, FROD_AREA_DIMS)
            frod, _, _ = frod_loc.find_object(frod_frame)
            if not frod:
                state = State.load_bait
            else:
                catch_frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
                catch, _ = catch_loc.find_object(catch_frame, imageprocessor.CATCH_CIRCLE_R)
                if catch:
                    x, y, r = catch
                    bstacks.click(CATCH_AREA_POINTS, (x, y))
        sleep(1/args.fps)