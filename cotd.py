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
FIRST_BAIT_APOS = (132, 586) # by 74 inc-x

CATCH_AREA_POINTS = 500, 130
CATCH_AREA_DIMS = 475, 350

FROD_AREA_POINTS = 230, 532
FROD_AREA_DIMS = 74, 74

class State(Enum):
    pick_bait = 0
    waiting = 1
    snagging = 2

class _Fisher:
    def __init__(self, template, thresh, params):
        #self.fge = imageprocessor.ForegroundExtractor([])
        self.md = imageprocessor.MoonDestroyer()
        self.cvt = imageprocessor.CSConverter()
        self.cloc = imageprocessor.CircleLocator(params)
        self.tmatch = imageprocessor.TemplateMatcher(template, thresh)

    def snag(self, image):
        return self.tmatch.is_match(image)

    def spot(self, image): 
        #fg = self.fge.extract(image)
        imat = self.cvt.bgr2gray(image)#self.cvt.bgr2ihsv(image, 0)
        imat = self.md.destroy(imat)
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
    hcircles = config['HoughCircles']

    fps = int(general['FPS'])

    t_wait = int(threshold['Wait_Thresh'])
    t_frod = float(threshold['FRod_Thresh'])
    t_dstreak = int(threshold['Deadlock_Streak'])

    frod_temp = str(templates['FRod_Template'])

    hc_params = []

    hc_params.append(int(hcircles['Param1']))
    hc_params.append(int(hcircles['Param2']))
    hc_params.append(int(hcircles['Minr']))
    hc_params.append(int(hcircles['Maxr']))

    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug",
        help="turns on debug mode", action="store_true")
    parser.add_argument("-V", "--verbose",
        help="shows state and compute time of \
                compute-intensive functions", type=int, default=1)
    parser.add_argument("-I", "--index",
        help="uses specified bait index as bait", type=int, default=1)
    parser.add_argument("-R", "--rounds",
        help="defines the number of iterations to run", type=int, default=sys.maxsize)
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
        print("\tBait index: %d" % args.index)
        print("\tFishing rounds: %d" % args.rounds)
    
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
    fisher = _Fisher(frod_path, t_frod, hc_params)
    canvas = None
    sess_round = 0

    if args.debug:
        cw, ch = CATCH_AREA_DIMS
        canvas = imageprocessor.Canvas("debug", cw, ch)
   
    while True and (sess_round <= args.rounds):
        if args.verbose == 1:
            if prev_state != state:
                logger.info(str(state))
            prev_state = state

        if args.debug:
            frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
            canvas.store(frame)
            spot = fisher.spot(frame)
            if spot is not None:
                canvas.draw_circle(spot)
            canvas.display()
            
        if state == State.pick_bait:
            time_ref = datetime.now()
            frame = bstacks.screenshot2mat(CATCH_AREA_POINTS, CATCH_AREA_DIMS)
            spot = fisher.spot(frame)
            if spot is not None:
                sess_round = sess_round + 1
                if sess_round > args.rounds:
                    break
                logger.info("Fishing Round: %d", sess_round)
                bx, by = FIRST_BAIT_APOS
                bx = bx + ((args.index - 1) * 74)
                bstacks.click((bx, by))
                x, y, r = spot
                bstacks.click(CATCH_AREA_POINTS, (x,y))
                state = State.waiting

        elif state == State.waiting:
            delta = datetime.now() - time_ref
            seconds = delta.total_seconds()
            if (seconds) > t_wait:
                dstreak = dstreak + 1
                sess_round = sess_round - 1
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

    print("")
    logger.info("Program Terminated with code: 0")