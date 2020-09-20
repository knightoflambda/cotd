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
FIRST_BAIT_APOS = (133, 586) #101, 553:65x65 + 11x65

CATCH_AREA_POINTS = 500, 130
CATCH_AREA_DIMS = 475, 350

FROD_AREA_POINTS = 230, 532
FROD_AREA_DIMS = 74, 74

class State(Enum):
    pick_bait = 0
    waiting = 1
    snagging = 2

class _Fisher:
    def __init__(self, template, thresh):
        self.fge = imageprocessor.ForegroundExtractor([])
        self.cvt = imageprocessor.CSConverter()
        self.cloc = imageprocessor.CircleLocator()
        self.tmatch = imageprocessor.TemplateMatcher(template, thresh)

    def snag(self, image):
        return self.tmatch.is_match(image)

    def spot(self, image): 
        fg = self.fge.extract(image)
        imat = self.cvt.bgr2ihsv(fg, 1)
        circle = self.cloc.locate(imat)

        return circle


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

    t_wait = int(threshold['Wait_Thresh'])
    t_frod = float(threshold['FRod_Thresh'])
    t_dstreak = int(threshold['Deadlock_Streak'])

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
        print("\tDeadlock Streak Threshold: %s" % t_dstreak)
    
    print("\n")
    sys.stdout.flush()
    
    # initialize tools
    bstacks = Window("BlueStacks")
    bstacks.fix_wpos()
    logger.info("Window repositioned")
    frod_path = "./res/{}.jpg".format(frod_temp)
    
    # initialize variables
    prev_state = None
    state = State.pick_bait
    time_ref = None
    db_disp = None
    dstreak = 0
    fisher = _Fisher(frod_path, t_frod)
   
    while True:
        if args.verbose == 1:
            if prev_state != state:
                logger.info(str(state))
            prev_state = state
        
        if state == State.pick_bait:
            time_ref = datetime.now()
            frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
            spot = fisher.spot(frame)
            if spot is not None:
                bstacks.click(FIRST_BAIT_APOS)
                x, y, r = spot
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
                state = State.pick_bait

            frame = bstacks.screenshot2mat(FROD_AREA_POINTS, FROD_AREA_DIMS)
            snag = fisher.snag(frame)
            if snag:
                dstreak = 0
                state = State.snagging
        elif state == State.snagging:
            snag_frame = bstacks.screenshot2mat(FROD_AREA_POINTS, FROD_AREA_DIMS)
            snag = fisher.snag(snag_frame)
            if not snag:
                state = State.pick_bait
            else:
                spot_frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
                spot = fisher.spot(spot_frame)
                if spot is not None:
                    x, y, r = spot
                    bstacks.click(CATCH_AREA_POINTS, (x, y))
            
        sleep(1/fps)