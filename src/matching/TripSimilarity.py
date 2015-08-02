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
    @route1: first trip (usually the complete one ~training)
    @route2: second trip (usually the incomplete one ~testing)
    @output: pair of point [pi, pj]
"""
def findPoDD(route1, route2, distFunc='haversine'):
    for j in range(0,len(route2)-1):
        pj = route2[j]
        dist = []
        for i in range(0,len(route1)-1):
            pi = route1[i]
            dCur = getGPSDistance(pj, pi, func=distFunc)
            dist.append(dCur)
            if len(dist) >= 3:
                if dist[-1] < dist[-2] and dist[-2] < dist[-3]:
                    print dist[-3:], i, j
                    return [pi, pj]
    print len(route1)
    print len(route2)
    print dist
    return [None, None]


""" Given two trips, they are similar if once they get close (at any point of any of the two trips), the following point do not increase (more than MAX_VAR) the distance among them. 
    @t1: first trip (usually the complete one ~training)
    @t2: second trip (usually the incomplete one ~testing)
    @MAX_VAR: maximum variance in km
    @N_POINTS: points in which compute the average distance of the trips (last N points of t2)
    @output: similarity (average distance of the last )
"""
def decreasingDistanceSim(t1, t2, MAX_VAR=.5):
    [p1, p2] = findPoDD(t1, t2)
    if p1 is None:
        return -1
    # compute distance
    print 'found PoDD in (%f,%f) ~ (%f,%f)' %(p1.lat, p1.lng, p2.lat, p2.lng)
        return 0.1