import argparse
import threading
import imageprocessor
import logging
import sys
import configparser

from windowwrapper import Window
from enum import Enum
from time import sleep
from datetime import datetime

VERSION = "RISTRETTO (v0.6)"
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

    config = configparser.ConfigParser()
    config.read('cotd.cfg')

    general = config['General']
    threshold = config['Threshold']
    templates = config['Templates']

    fps = int(general['FPS'])
    bait_style = str(general['Bait_Style'])

    t_wait = int(threshold['Wait_Thresh'])
    t_frod = float(threshold['FRod_Thresh'])
    t_bait = float(threshold['Bait_Thresh'])
    t_dstreak = int(threshold['Deadlock_Streak'])

    cr_temp = str(templates['CR_Template'])
    frod_temp = str(templates['FRod_Template'])

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug",
        help="turns on debug mode", action="store_true")
    parser.add_argument("-v", "--verbose",
        help="shows state and compute time of \
                compute-intensive functions", type=int, default=1)
    args = parser.parse_args()

    print("\nPetPals - Catch of the Day")
    print("Author: l4mbda")
    print("Program Version: %s" % VERSION)
    print("\nJob 1:21\tthe LORD gave, and the LORD hath taken away;\n\t\tblessed be the name of the LORD\n")
    print("\nPsalm 115:1\tNot unto us, O Lord, not unto us, \n\t\tbut unto thy name give glory,\n\t\tfor thy mercy, and for thy truth's sake.\n")
    print("\nJames 1:17\tEvery good and perfect gift is from above,\n\t\tcoming down from the Father of the heavenly lights\n")

    if args.verbose == 1:
        print("Running with params: ")
        print("\tFPS: %d" % fps)
        print("\tDebug Mode: %s" % args.debug)
        print("\tVerbose Level: %d" % args.verbose)
        print("\tBaiting Style: %s" % bait_style)
        print("\tDeadlock Streak Threshold: %s" % t_dstreak)
    
    print("\n")
    sys.stdout.flush()
    
    # initialize tools
    bstacks = Window("BlueStacks")
    bstacks.fix_wpos()
    logger.info("Window repositioned")
    catch_region_path = "./res/{}.jpg".format(cr_temp)
    frod_path = "./res/{}.jpg".format(frod_temp)
    if bait_style != "first":
        bait_path = "./res/{}.jpg".format(bait_style)
    
    bait_coords_center = ()
    if bait_style != "first":
        bait_loc = imageprocessor.TemplateMatchLocator([(bait_path, t_bait)])
    frod_loc = imageprocessor.TemplateMatchLocator([(frod_path, t_frod)])
    catch_loc = imageprocessor.CircleLocator(catch_region_path)

    # initialize variables
    prev_state = None
    state = State.load_bait
    time_ref = None
    db_disp = None
    canvas = None

    dstreak = 0
    if args.debug:
        db_disp = imageprocessor.ImageDisplay("debug", (0, 600))
        canvas = imageprocessor.Canvas()

    import cv2 as cv
    import numpy as np
    # test data
    colors = [ # bgr format
        [229, 215, 133],
        [237, 231, 156],
        [244, 241, 180], 
        [255, 253, 241], # +-5
        [254, 247, 214],
        [255, 234, 182],
        [222, 216, 87],
        [167, 146, 64],
        [195, 181, 68],
        # left - up
        [134, 65, 56],
        [224, 208, 201],
        [237, 232, 231],
        [192, 167, 157]
    ]
    
    while True:
        if args.verbose == 1:
            if prev_state != state:
                logger.info(str(state))
            prev_state = state
        
        if args.debug:
            frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
            width, height = CATCH_AREA_DIMS
            masks = np.zeros((height,width), np.uint8)
            for color in colors:
                mask = cv.inRange(frame, np.array([x - 3 for x in color]), np.array([x + 3 for x in color]))
                masks = cv.bitwise_or(masks, mask)

            frame[masks > 0] = (0,0,0)
            #catch, cmat = catch_loc.find_object(frame, imageprocessor.CATCH_CIRCLE_R)
            #catch = canvas.draw_circle(cmat, imageprocessor.CATCH_CIRCLE_R)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2HSV)[:, :, 1]
            #kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(5,5))
            #gray = cv.erode(gray,kernel,iterations = 1)
            circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1.2, 1000, None, 50, 30, 30, 35)
            if circles is not None:
                circles = np.round(circles[0, 0, :]).astype("int")
                x, y, r = circles
                frame = cv.circle(frame, (x, y), r, (0, 0, 255), 2)
            db_disp.set_image(frame)

        else:
            if state == State.load_bait:
                time_ref = datetime.now()
                frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
                catch, _ = catch_loc.find_object(frame, imageprocessor.CATCH_CIRCLE_R)
                if catch:
                    if bait_style == "first":
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
                                    logger.info("%s found in index %d, %.2f%% match", bait_style, i, res)
                                bait_coords_center = (x + 32, y + 32)
                                break
                    bstacks.click(bait_coords_center)
                    x, y, r = catch
                    bstacks.click(CATCH_AREA_POINTS, (x,y))
                    state = State.waiting
            elif state == State.waiting:
                delta = datetime.now() - time_ref
                seconds = delta.total_seconds()
                if (seconds) > t_wait:
                    dstreak = dstreak + 1
                    if dstreak > t_dstreak: 
                        logger.info("Deadlock threshold passed, quitting program...")
                        break
                    if args.verbose == 1:
                        logger.info("Deadlocked in wait, ({} of {}) resetting state...".format(dstreak, t_dstreak))
                    state = State.load_bait

                frame = bstacks.screenshot2mat(FROD_AREA_POINTS, FROD_AREA_DIMS)
                frod, _, _ = frod_loc.find_object(frame)
                if frod:
                    dstreak = 0
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
            
        sleep(1/fps)