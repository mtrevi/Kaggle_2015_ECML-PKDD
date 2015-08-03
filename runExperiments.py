# -*- coding: utf-8 -*-
"""
Trip object that contains all the information of a single individual trip. 
__source__ : 
__author__ : Michele Trevisiol @trevi
"""

import os
import csv
import sys
import time
import random
import cPickle as pickle
from optparse import OptionParser
# custom dependences
from src.objects.TripObj import *
from src.bbox.BBoxObj import *
from src.matching.TripSimilarity import *
from src.matching.DistanceMetrics import *

parser = OptionParser()
parser.add_option( '--train', dest='trainFile', default='data/train.1k.csv')
parser.add_option( '--test', dest='testFile', default='data/test.csv')
parser.add_option( '--bbox', dest='bboxFile', default='data/train.1k.bbox.p')
parser.add_option( '--split', dest='split', default=0.75)
parser.add_option( '-d', action="store_true", dest="devel")

# ---------------- 
# Load Parameters
(options, args) = parser.parse_args()
TRAINFILE = options.trainFile
TESTFILE = options.testFile
BBOXFile = options.bboxFile
SPLIT = float(options.split)
DEVEL = options.devel
MAX_DIST_TOLERATE = 5


# ---------------- 
# Load Data
trips = {}
errCnt = 0
print >> sys.stderr, 'Loading train set from %s' %TRAINFILE
with open(TRAINFILE, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        try:
            trip = TripObj(row)
            trips[trip.id] = trip
        except Exception, err:
            if errCnt > 0:
                sys.stderr.write('ERROR: %s (%d loaded)\n' % (str(err),len(trips)) )
            errCnt += 1
print >> sys.stderr, '\t loaded %d trips (%d errors)' %(len(trips),errCnt-1)


# ---------------- 
# Build (or load if already built) the bbox with final destination
if os.path.isfile(BBOXFile):
    print >> sys.stderr, 'Loading BBox Data from %s' %BBOXFile
    BBox = pickle.load( open(BBOXFile,"rb") )
    print >> sys.stderr, '\t loaded %d coordinates' %len(BBox.lats)
else:
    print >> sys.stderr, 'Computing BBox Data'
    BBox = BBoxObj()
    BBox.loadTrainDestinations(trips)
    print >> sys.stderr, '\t loaded %d coordinates' %len(BBox.lats)
    print >> sys.stderr, '\t sorting lists and dictionaries'
    BBox.sortLatsLngs()
    pickle.dump( BBox, open(BBOXFile,"wb") )
    print >> sys.stderr, '\t saving BBox Data to %s' %BBOXFile


# ---------------- 
# Split into train and test set
print >> sys.stderr, 'Splitting into train and test set'
trainSize = int( SPLIT*len(trips) )
shuffleIds = trips.keys()
random.shuffle(shuffleIds)
trainIds = shuffleIds[:trainSize]
testIds = shuffleIds[trainSize:]
print >> sys.stderr, '\t gotta %d train trips, %d test trips (over %d total trips)' \
%(len(trainIds), len(testIds), len(trips))


# ---------------- 
# For DEVELOPMENT : Convert test set into a validation set (remove final GPS locations)
if DEVEL:
    skipTrips = 0
    print >> sys.stderr, '[DEVELOPMENT] Convert "fake" train set into a validation set'
    for ttId in testIds:
        KEEP = random.uniform(.7, .9) # keep rnd(0.7-0.9) percent of the trip location
        tt = trips[ttId]
        # recude location data available
        locDataSize = len(tt.route)
        if locDataSize <= 5: # cannot work with too few data points
            skipTrips += 1
            continue
        locDataKeep = int(round(KEEP*locDataSize))
        tt.route = tt.route[:locDataKeep]
        # print '\t from %d data points, we keep %d points' %(locDataSize, len(tt.route))
print '\t Reduced routes of %d test trips (%d skip because of too few data points)' \
%(len(testIds)-skipTrips, skipTrips)


# ---------------- 
# Run NN and prediction of destination
# TODO : instead of comparing with each individual train_route, group them before by ending point
# TODO : when the points are going forther that the last destination, just compute a regression line and set a point not too far (estimate the missing points ~10-20% and their total distance)
stTot = time.time()
print 'Parsing test trips...'
testError = []
n = 0
noTESTS = len(testIds)
for ttestId in testIds:
    st = time.time()
    ttest = trips[ttestId]
    n += 1
    print '[%d] Id:' %n, ttest.id,
    # Find BBox and get only routes that end in that BBox
    area, lat, lng = findDestinationBBox(ttest, tolerance=True)
    trainCandidatesIds = BBox.getCandidatesIds(area, lat, lng)
    #
    candidates = {} # score -> ttrain
    for ttrainId in trainCandidatesIds:
        ttrain = trips[ttrainId]
        C = slopeDistanceSim(ttest.route, ttrain.route, 0.5)
        noCommP = float(C.noPj)/C.noPi
        if C.wrongDirection > .4 or C.commPoints < .1 or C.slope >= 0:
            continue
        # if trainTrip.destination is too far from last point of testTrip, skip it
        candDist = haversineDist(ttest.route[-1], ttrain.destination)
        if candDist > MAX_DIST_TOLERATE:
            continue
        # save candidate
        candidates[C.avgMagnitude] = [ttrain, C]
        # ttest.printRoute()
        # ttrain.printRoute()
        # print ttest.id, ttrain.id, d
    # if no candidates
    if len(candidates) == 0:
        'TODO'
        fakePrediction = ttest.route[-1]
        gtErr = haversineDist(ttest.destination, fakePrediction)
        testError.append(gtErr)
        print '\t curError: %f totError: %f \t(%d/%d trainCand) ~%.2fs %s' \
        %(gtErr, np.mean(testError),len(candidates),len(trainCandidatesIds),time.time()-st,'NO CANDIDATES')
        continue
    # get smallest scores
    gtErr = haversineDist(ttest.destination, candidates[sorted(candidates)[0]][0].destination)
    testError.append(gtErr)
    # print stats
    topn = 0
    for score in sorted(candidates):
        #
        gtErr = haversineDist(ttest.destination, candidates[score][0].destination)
        if topn > 0:
            print "score: %f, %s, finalDist: %f" \
            %(score, candidates[score][1].serialize(), gtErr)
            topn -= 1
        if topn <= 0:
            break
    # print stats
    print '\t curError: %f totError: %f \t(%d/%d trainCand) ~%.2fs' \
    %(gtErr, np.mean(testError),len(candidates),len(trainCandidatesIds),time.time()-st)
    #
    if n >= noTESTS:
        break
print 'Tested %d trips, %d with estimation (error: %f) and %d missed \t~%.2fs' \
%(noTESTS, len(testError), np.mean(testError), noTESTS-len(testError), time.time()-stTot)

# ---------------- 
# Evaluate
