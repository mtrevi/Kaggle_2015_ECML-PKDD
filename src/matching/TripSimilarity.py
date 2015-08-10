# -*- coding: utf-8 -*-
"""
__author__ : Michele Trevisiol @trevi
__description__ : Trip Similarity contains a collection of similarity approaches with the aim to measure the similarity between two given trips.
"""

import sys
import numpy as np
from scipy import stats
from DistanceMetrics import *
from ..objects.GPSPoint import *
from ..objects.CandidateObj import *


""" Given a point pi find closest point in route2.
    From this the comparison with the test route will begin.
"""
def findClosestPoint(pi, route2, distFunc):
    minDist = 9999
    for j in range(0,len(route2)):
        pj = route2[j]
        d = getGPSDistance(pi, pj, func=distFunc)
        if d < minDist:
            minDist = d
            info = [pj, j]
    return info[0], info[1], minDist


''' TODO : rewrite description '''
""" Given two trips, find the Points of Decreasing Distance. This are the points p_{i} (\in t1) and p_{j} (\in t2) for which the distance among them is lower than the distance among the previous pair of points (p_{i-1},p_{j-1}) which distance is lower than the ones among the previour pair of points (p_{i-2},p_{j-2}).
    @route1: first trip (usually the complete one ~training)
    @route2: second trip (usually the incomplete one ~testing)
    @MAX_VAR: maximum variance in km
    @output: pair of point [pi, pj]
"""
def findOverlapingPath(route1, route2, MAX_VAR, distFunc, MAGNITUDE):
    distPP = []
    wrongDirection = 0
    higherDistance = 0
    for i in range(0,len(route1)):
        pi = route1[i]
        pj, j, d = findClosestPoint(pi, route2, distFunc)
        if len(distPP) > 0: 
            if j < distPP[-1][1]:
                wrongDirection += 1
            if d > (distPP[-1][2]+MAX_VAR):
                higherDistance += 1
        if higherDistance > 0:
            break
        distPP.append( [i, pi, j, pj, d] )
    # print 'wrongDirectionAlert:', wrongDirectionAlert
    # compute avg magnitude of last two distances
    avgMagnitude = 0.0
    if len(distPP) > 2:
        if MAGNITUDE == 2:
            avgMagnitude = np.mean( [distPP[-1][4],distPP[-2][4]] )
        elif MAGNITUDE == 3:
            avgMagnitude = np.mean( [distPP[-1][4],distPP[-2][4],distPP[-3][4]] )
        elif MAGNITUDE == 4 and len(distPP) >= 4:
            avgMagnitude = np.mean( [distPP[-1][4],distPP[-2][4],distPP[-3][4],distPP[-4][4]] )
        elif MAGNITUDE >= 5 and len(distPP) >= 4:
            avgMagnitude = np.mean( [distPP[-1][4],distPP[-2][4],distPP[-3][4],distPP[-4][4],distPP[-5][4]] )
    # 
    return distPP, wrongDirection, higherDistance, avgMagnitude

""" 
"""
def getCommPoints(distPP):
    prevJ = -1
    diffJ = []
    for step in distPP:
        i = step[0]
        j = step[2]
        if prevJ < 0:
            prevJ = j
            continue
        if j != prevJ:
            if len(diffJ) == 0:
                diffJ.append(prevJ)
            diffJ.append(j)
            prevJ = j
    if len(diffJ) == 0:
        return 0.0
    return float(len(set(diffJ)))/len(diffJ)


""" Given two trips, they are similar if once they get close (at any point of any of the two trips), the following point do not increase (more than MAX_VAR) the distance among them. 
    @route1: first trip (usually the complete one ~training)
    @route2: second trip (usually the incomplete one ~testing)
    @MAX_VAR: maximum variance in km
    @N_POINTS: points in which compute the average distance of the trips (last N points of t2)
    @output: similarity (average distance of the last )
"""
def slopeDistanceSim(route1, route2, MAX_VAR=.5, MAGNITUDE=3, distFunc='haversine'):
    distPP, wrongDirection, higherDistance, avgMagnitude = findOverlapingPath(route1, route2, MAX_VAR, distFunc, MAGNITUDE)
    routeSim = 0.0
    newCandidate = CandidateObj()
    if higherDistance > 0:
        return newCandidate
    else:
        newCandidate.wrongDirection = wrongDirection
        newCandidate.higherDistance = higherDistance
        newCandidate.avgMagnitude = avgMagnitude
    # prepare x and y
    x = []
    y = []
    uniquePj = set()
    for i in range(0,len(distPP)):
        x.append(i)
        y.append(distPP[i][4])
        uniquePj.add(distPP[i][2])
    try:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    except:
        slope = -0.001
    # get common points once the firt pj is changing
    commPoints = getCommPoints(distPP)
    # normalize the alerts
    wrongDirectionAlert = float(wrongDirection)/len(route1)
    higherDistanceAlert = float(higherDistance)/len(route1)
    # save info
    newCandidate.slope = slope
    newCandidate.noPj = len(uniquePj)
    newCandidate.noPi = len(route1)
    newCandidate.commPoints = commPoints
    # 
    return newCandidate