# -*- coding: utf-8 -*-
"""
Trip Similarity contains a collection of similarity metrics 
with the aim to evaluate the "distance" between two given trips.
__source__ : 
__author__ : Michele Trevisiol @trevi
"""

import sys
from DistanceMetrics import *
from ..objects.GPSPoint import *


''' TODO : extend to 3 points  '''
""" Given two trips, find the Points of Decreasing Distance. This are the point p_{i} (\in t1) and p_{j} (\in t2) for which the distance among them is lower than the distance among the previous pair of points (p_{i-1},p_{j-1}) which distance is lower than the ones among the previour pair of points (p_{i-2},p_{j-2}).
    @t1: first trip (usually the complete one ~training)
    @t2: second trip (usually the incomplete one ~testing)
    @output: pair of point [pi, pj]
"""
def findPoDD(t1, t2, distFunc='haversine'):
    for j in range(0,len(t2)-1):
        pj = t2[j]
        dPrev = -1
        for i in range(0,len(t1)-1):
            pi = t1[i]
            dCur = getGPSDistance(pj, pi, func=distFunc)
            if dPrev < 0:
                dCur = dPrev
            elif dCur < dPrev:
                return [pi, pj]
    return [GPSPoint([-1,-1]), GPSPoint([-1,-1])]


""" Given two trips, they are similar if once they get close (at any point of any of the two trips), the following point do not increase (more than MAX_VAR) the distance among them. 
    @t1: first trip (usually the complete one ~training)
    @t2: second trip (usually the incomplete one ~testing)
    @MAX_VAR: maximum variance in km
    @N_POINTS: points in which compute the average distance of the trips (last N points of t2)
    @output: similarity (average distance of the last )
"""
def decreasingDistanceSim(t1, t2, MAX_VAR=.5):
    [p1, p2] = findPoDD(t1, t2)
    print 'found PoDD in (%f,%f) ~ (%f,%f)' %(p1.lat, p1.lng, p2.lat, p2.lng)