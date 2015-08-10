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
import operator
import cPickle as pickle
from optparse import OptionParser
# multithreading done with:
# https://pythonhosted.org/joblib/parallel.html
# http://glowingpython.blogspot.co.uk/2014/05/code-parallelization-with-joblib.html
from joblib import Parallel, delayed
import multiprocessing
# custom dependences
from src.objects.TripObj import *
from src.objects.GPSPoint import *
from src.bbox.BBoxObj import *
from src.bbox.GridObj import *
from src.matching.TripSimilarity import *
from src.matching.DistanceMetrics import *

parser = OptionParser()
parser.add_option( '--train', dest='trainFile', default='data/train.csv')
parser.add_option( '--test', dest='testFile', default='data/test.csv')
parser.add_option( '--bbox', dest='bboxFile', default='data/train.bbox.p')
parser.add_option( '--grid', dest='gridFile', default='data/train.grid.p')
parser.add_option( '--out', dest='outFile', default='data/test.pred.csv')
parser.add_option( '--split', dest='split', default=0.75)
parser.add_option( '-d', action="store_true", dest="devel")
parser.add_option( '--cpu', dest="Ncpu", default=1)
# parameters
parser.add_option( '--max-airport-distance', dest='maxAirportDist', default='2.0')
parser.add_option( '--max-distance', dest='maxDistTolerate', default='1.5')
parser.add_option( '--max-loop-distance', dest='maxLoopDist', default='0.8')
parser.add_option( '--max-var', dest='maxVariance', default='0.3')
parser.add_option( '--bbox-tolerance', dest='bboxTolerance', default='.01')
parser.add_option( '--magnitude', dest='magnitude', default='3')
parser.add_option( '--last_cells', dest='lastCells', default='0')
parser.add_option( '--topn', dest='topN', default='4')

# ---------------- 
# Load Parameters
(options, args) = parser.parse_args()
TRAINFILE = options.trainFile
TRAINFILEP = options.trainFile.replace('csv','p')
TESTFILE = options.testFile
BBOXFile = options.bboxFile
GRIDFile = options.gridFile
SPLIT = float(options.split)
DEVEL = options.devel
NCPU = int(options.Ncpu)
l_MAX_AIRPORT_DIST = [float(i) for i in options.maxAirportDist.strip().split(',')]
l_MAX_DIST_TOLERATE = [float(i) for i in options.maxDistTolerate.strip().split(',')]
l_MAX_LOOP_DIST = [float(i) for i in options.maxLoopDist.strip().split(',')]
l_BBOX_TOLERANCE = [float(i) for i in options.bboxTolerance.strip().split(',')]
l_MAX_VARIANCE = [float(i) for i in options.maxVariance.strip().split(',')]
l_LAST_CELLS = [int(i) for i in options.lastCells.strip().split(',')]
l_TOPN = [int(i) for i in options.topN.strip().split(',')]
l_MAGNITUDE = [int(i) for i in options.magnitude.strip().split(',')]
# check last cell
if len(l_LAST_CELLS) == 1:
    LAST_CELLS = int(l_LAST_CELLS[0])
#
# Edge Cases
airport = GPSPoint([41.237, -8.670]) #GPSPoint([41.242390, -8.678595])
portoCenter = GPSPoint([41.16, -8.63])
portoCampanha = GPSPoint([41.14864, -8.58572])



# ---------------- 
# Load Data
line = 0
trips = {}
errCnt = 0
emptyRoute = 0
st = time.time()
print >> sys.stderr, 'Loading train set from %s' %TRAINFILE
with open(TRAINFILE, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        line += 1
        try:
            trip = TripObj(row)
            # remove 1 length route
            if trip.destination is not None:
                trips[trip.id] = trip
            else:
                emptyRoute += 1
        except Exception, err:
            if errCnt > 0:
                sys.stderr.write('[line: %d] ERROR: %s (%d loaded)\n' \
                    % (line,str(err),len(trips)) )
                break
            errCnt += 1
print >> sys.stderr, '\t loaded %d trips (%d emptyRoute, %d errors) \t~%.2fs' \
%(len(trips),emptyRoute,errCnt-1,time.time()-st)


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
    print >> sys.stderr, '\t saving BBox Data to %s' %BBOXFile
    pickle.dump( BBox, open(BBOXFile,"wb") )
    print >> sys.stderr, '\t done.'


# ---------------- 
# Build (or load if already built) the GRID
if os.path.isfile(GRIDFile) and LAST_CELLS > 0:
    print >> sys.stderr, 'Loading Grid Data from %s' %GRIDFile
    Grid = pickle.load( open(GRIDFile,"rb") )
    print >> sys.stderr, '\t loaded %d cells' %Grid.noCells()
elif LAST_CELLS > 0:
    print >> sys.stderr, 'Computing Grid Data'
    Grid = GridObj()
    Grid.loadTrainRoutes(trips)
    print >> sys.stderr, '\t built %d cells' %Grid.noCells()
    print >> sys.stderr, '\t saving Grid Data to %s' %GRIDFile
    pickle.dump( Grid, open(GRIDFile,"wb") )
    print >> sys.stderr, '\t done.'
else:
    print >> sys.stderr, 'Skipping Grid Data Loader'


# ---------------- 
# Split into train and test set
if DEVEL:
    print >> sys.stderr, 'Splitting into train and test set'
    trainSize = int( SPLIT*len(trips) )
    # check size and fix if too big
    if len(trips)-trainSize > 500:
        trainSize = len(trips)-500
        print >> sys.stderr, '\t limited test size as 500'
    shuffleIds = trips.keys()
    random.shuffle(shuffleIds)
    trainIds = shuffleIds[:trainSize]
    testIds = shuffleIds[trainSize:]
    print >> sys.stderr, '\t gotta %d train trips, %d test trips (over %d total trips)' \
    %(len(trainIds), len(testIds), len(trips))
else:
    trainIds = trips.keys()
    testIds = []
    errCnt = 0
    print >> sys.stderr, 'Loading test set from %s' %TESTFILE
    with open(TESTFILE, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                trip = TripObj(row)
                trips[trip.id] = trip
                testIds.append(trip.id)
            except Exception, err:
                if errCnt > 0:
                    sys.stderr.write('ERROR: %s (%d loaded)\n' % (str(err),len(testIds)) )
                errCnt += 1
    print >> sys.stderr, '\t loaded %d tests trips (%d total, %d errors)' \
    %(len(testIds),len(trips),errCnt-1)


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
# Run NN and destination prediction
def predictDestination(n, ttestId):
    st = time.time()
    ttest = trips[ttestId]
    method = 'matching'
    # 
    # edge cases
    candDest = None
    airport_last_d = getGPSDistance(ttest.route[-1], airport)
    airport_first_d = getGPSDistance(ttest.route[0], airport)
    portoCampanha_last_d = getGPSDistance(ttest.route[-1], portoCampanha)
    portoCampanha_first_d = getGPSDistance(ttest.route[0], portoCampanha)
    # if the trip has only one point (near the airport) recommend citycenter
    # if len(ttest.route) == 1 and airport_first_d < MAX_AIRPORT_DIST:
    #     candDest = portoCenter
    #     method = 'fromAIRPORT'
    if airport_last_d <= MAX_AIRPORT_DIST and airport_first_d > airport_last_d-0.3:
        candDest = airport
        method = 'toAIRPORT'
    elif portoCampanha_last_d <= (MAX_AIRPORT_DIST-1) and portoCampanha_first_d > portoCampanha_last_d:
        candDest = portoCampanha
        method = 'toPORTOCAMPANHA'
    # if cab forgot to turn off the GPS and is coming back: recommend first location
    if len(ttest.route) > 4:
        mid_point = ttest.route[len(ttest.route)/2]
        d_mid_last0 = getGPSDistance(mid_point,ttest.route[-1])
        d_0_last0 = getGPSDistance(ttest.route[0],ttest.route[-1])
        d_0_last1 = getGPSDistance(ttest.route[0],ttest.route[-2])
        d_0_last2 = getGPSDistance(ttest.route[0],ttest.route[-3])
        if d_0_last0 <= d_0_last1 and d_0_last0 <= d_0_last2 and d_0_last0 <= MAX_LOOP_DIST and d_0_last0 < d_mid_last0:
            candDest = ttest.route[0]
            method = 'LOOP'
    #
    # Find BBox and get only routes that end in that BBox
    area, lat, lng = findDestinationBBox(ttest, tolerance=BBOX_TOLERANCE)
    trainCandidatesIds = BBox.getCandidatesIds(area, lat, lng)
    #
    candidates = {} # score -> ttrain
    if candDest is None:
        for ttrainId in trainCandidatesIds:
            ttrain = trips[ttrainId]
            C = slopeDistanceSim(ttest.route, ttrain.route, MAX_VARIANCE)
            noCommP = float(C.noPj)/C.noPi
            if C.wrongDirection > .4 or C.commPoints < .1 or C.slope >= 0:
                continue
            # if trainTrip.destination is too far from last point of testTrip, skip it
            candDist = getGPSDistance(ttest.route[-1], ttrain.destination)
            if candDist > MAX_DIST_TOLERATE:
                continue
            # save candidate
            candidates[C.avgMagnitude] = [ttrain, C]
    # ----------
    # CHECK
    # ----------
    # if no candidates
    if len(candidates) < TOPN and LAST_CELLS > 1:
        newCandidates = Grid.getGridCandidates(ttest.route, LAST_CELLS) # return list of trainId
        if len(newCandidates) > 0:
            method = '+GRID'
            # add new candidates to the main candidates with the lower score
            for tId in newCandidates:
                ttrain = trips[tId]
                # if trainTrip.destination is too far from last point of testTrip, skip it
                C = slopeDistanceSim(ttest.route, ttrain.route, MAX_VARIANCE)
                candDist = getGPSDistance(ttest.route[-1], ttrain.destination)
                if candDist > MAX_DIST_TOLERATE:
                    continue
                # save candidate
                candidates[C.avgMagnitude] = [ttrain, C]
    #   
    # if (again) no candidates
    if len(candidates) == 0:
        if candDest is None:
            candDest = ttest.route[-1]
            method = 'lastPOINT'
    elif len(candidates) <= 2:
        # pick the first ranked
        candDest = candidates[sorted(candidates)[0]][0].destination
        method = 'only2candidates-pickFIRST'
    else:
        # MEDOID over the TOPN
        distances = {}
        candidatesKeys = sorted(candidates)
        topnCandidatesKeys = candidatesKeys[:TOPN]
        for i in range(0,len(topnCandidatesKeys)-1):
            ki = topnCandidatesKeys[i]
            cand_i = candidates[ki][0]
            for j in range(i+1,len(topnCandidatesKeys)):
                kj = topnCandidatesKeys[j]
                cand_j = candidates[kj][0]
                d_ij = getGPSDistance(cand_i.destination, cand_j.destination)
                if not distances.has_key(cand_i.id):
                    distances[cand_i.id] = []
                if not distances.has_key(cand_j.id):
                    distances[cand_j.id] = []
                distances[cand_i.id].append(d_ij)
                distances[cand_j.id].append(d_ij)
        distancesMean = {}
        for candId in distances:
            distancesMean[candId] = np.mean(distances[candId])
        selectedCandId = min(distancesMean.iteritems(), key=operator.itemgetter(1))[0]
        candDest = trips[selectedCandId].destination
        if method == '+GRID':
            method = 'matching+MEDOID+GRID'
        else:
            method = 'matching+MEDOID'
    #
    # print stats
    if DEVEL:
        gtErr = getGPSDistance(ttest.destination, candDest)
        print >> sys.stderr, '[%s] Id:%s \t curError: %f (%d/%d trainCand) method: %s\t ~%.2fs' \
        %(n,ttest.id,gtErr,len(candidates),len(trainCandidatesIds),method,time.time()-st)
    else:
        print >> sys.stderr, '[%s] Id:%s \t candDest: (%f,%f)\t method: %s' \
        %(n,ttest.id,candDest.lat,candDest.lng,method)
    #
    res = '"%s",%f,%f' %(ttest.id,candDest.lat,candDest.lng)
    return res



""" This part of the code is extremely hugly I know. However it is just a quick trick to perform multiple experiments with different parameters without re-loading the training set each time.
"""
for MAX_AIRPORT_DIST in l_MAX_AIRPORT_DIST:
    for MAX_DIST_TOLERATE in l_MAX_DIST_TOLERATE:
        for MAX_LOOP_DIST in l_MAX_LOOP_DIST:
            for BBOX_TOLERANCE in l_BBOX_TOLERANCE:
                for MAX_VARIANCE in l_MAX_VARIANCE:
                    for LAST_CELLS in l_LAST_CELLS:
                        for TOPN in l_TOPN:
                            for MAGNITUDE in l_MAGNITUDE:
                                SUFFIX = 'mad%.1f_mdt%.1f_mld%.1f_mv%.1f_bbt%.2f_lc%d_topn%d_m%d' %(MAX_AIRPORT_DIST,MAX_DIST_TOLERATE,MAX_LOOP_DIST,MAX_VARIANCE,BBOX_TOLERANCE,LAST_CELLS,TOPN,MAGNITUDE)
                                OUTFILE = options.outFile.replace('csv','%s.csv'%SUFFIX)
                                # Main Loop
                                stTot = time.time()
                                print >> sys.stderr, 'Parsing test trips...'
                                testError = []
                                outResults = open( OUTFILE, 'w+' )
                                outResults.write('TRIP_ID,LATITUDE,LONGITUDE\n')
                                #
                                parallelizer = Parallel(n_jobs=NCPU)
                                tasks_iterator = ( delayed(predictDestination)(i,testIds[i]) for i in range(0,len(testIds)) )
                                allPred = parallelizer( tasks_iterator )
                                for line in allPred:
                                    outResults.write('%s\n' %line.strip())
                                    if DEVEL:
                                        b = line.split(',')
                                        tId = b[0].replace('"','')
                                        lat = float(b[1])
                                        lng = float(b[2])
                                        predDest = GPSPoint([lat,lng])
                                        gtErr = haversineDist(trips[tId].destination, predDest)
                                        testError.append(gtErr)
                                # print allPred
                                if DEVEL:
                                    print >> sys.stderr, 'avgError: %f' %np.mean(testError)
                                print >> sys.stderr, 'Computational Time ~%.2f seconds' %(time.time()-stTot)
                                outResults.flush()
                                outResults.close()