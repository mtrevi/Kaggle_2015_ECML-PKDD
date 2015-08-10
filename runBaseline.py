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

parser = OptionParser()
parser.add_option( '--test', dest='testFile', default='data/test.csv')
parser.add_option( '--out', dest='outFile', default='data/test.pred.csv')

# ---------------- 
# Load Parameters
(options, args) = parser.parse_args()
TESTFILE = options.testFile
OUTFILE = options.outFile


# ---------------- 
# Load test set
errCnt = 0
trips = {}
print >> sys.stderr, 'Loading test set from %s' %TESTFILE
with open(TESTFILE, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        try:
            trip = TripObj(row)
            trips[trip.id] = trip
        except Exception, err:
            if errCnt > 0:
                sys.stderr.write('ERROR: %s (%d loaded)\n' % (str(err),len(trips)) )
            errCnt += 1
print >> sys.stderr, '\t loaded %d tests trips (%d total, %d errors)' \
%(len(trips),len(trips),errCnt-1)


# ---------------- 
# BASELINE : return last location as predicted destination
outResults = open( OUTFILE, 'w+' )
outResults.write('TRIP_ID,LATITUDE,LONGITUDE\n')
for ttest in trips.values():
    lastPoint = ttest.route[-1]
    outResults.write('"%s",%f,%f\n' %(ttest.id, lastPoint.lat, lastPoint.lng))
    #
outResults.flush()
outResults.close()