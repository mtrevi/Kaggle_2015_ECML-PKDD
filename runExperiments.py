# -*- coding: utf-8 -*-
"""
Trip object that contains all the information of a single individual trip. 
__source__ : 
__author__ : Michele Trevisiol @trevi
"""

import os
import csv
import sys
import random
import cPickle as pickle
from optparse import OptionParser
# custom dependences
from src.objects.TripObj import *
from src.matching.TripSimilarity import *

parser = OptionParser()
parser.add_option( '--train', dest='trainFile', default='data/train.1k.csv')
parser.add_option( '--test', dest='testFile', default='data/test.csv')
parser.add_option( '--split', dest='split', default=0.75)
parser.add_option( '-d', action="store_true", dest="devel")

# ---------------- 
# Load Parameters
(options, args) = parser.parse_args()
TRAINFILE = options.trainFile
TESTFILE = options.testFile
SPLIT = float(options.split)
DEVEL = options.devel


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
                sys.stderr.write('ERROR: %s\n' % str(err))
            errCnt += 1
print >> sys.stderr, '\t loaded %d trips (%d errors)' %(len(trips),errCnt-1)


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
print '\t Reduced routes of %d train trip (%d skip because of too few data points)' \
%(len(testIds)-skipTrips, skipTrips)


# ---------------- 
# Run NN and prediction of destination
# TODO : instead of comparing with each individual train_route, group them before by ending point
# TODO : when the points are going forther that the last destination, just compute a regression line and set a point not too far (estimate the missing points ~10-20% and their total distance)
for ttestId in testIds:
    ttest = trips[ttestId]
    candidates = {} # score -> ttrain
    for ttrainId in trainIds:
        ttrain = trips[ttrainId]
        d = decreasingDistanceSim(ttest.route, ttrain.route, 0.5)
        print ttest.printRoute()
        print ttrain.printRoute()
        print ttest.id, ttrain.id, d
        break
    break

# ---------------- 
# Evaluate
