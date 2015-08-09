# -*- coding: utf-8 -*-
"""
__source__ : 
__author__ : Michele Trevisiol @trevi
"""

import sys
import csv
import numpy as np
from ast import literal_eval
from ..objects.GPSPoint import *

class BBoxObj:

    def __init__(self):
        self.latIds = {}
        self.lngIds = {}
        self.lats = []
        self.lngs = []


    # ---------------- 
    # Loading Data
    # ---------------- 
    def loadTrainDestinations(self, trips):
        for tid in trips:
            t = trips[tid]
            lat = t.destination.lat
            lng = t.destination.lng
            # store
            self.latIds[lat] = t.id
            self.lngIds[lng] = t.id
            self.lats.append(lat)
            self.lngs.append(lng)


    def sortLatsLngs(self):
        self.lats = sorted(self.lats, key=float)
        self.lngs = sorted(self.lngs, key=float)


    # ---------------- 
    # Parsing Loaded Data
    # ---------------- 
    ''' Given a bbox, get routes (ids) that end in that bbox 
        @area: 1 means north-west, 2 means north-est, 3 means south-west, 4 means south-est
    '''
    def getCandidatesIds(self, area, lat, lng):
        if area == 1:
            idsByLat = self.getLatHigherThan(lat)
            idsByLng = self.getLngLowerThan(lng)
        elif area == 2:
            idsByLat = self.getLatHigherThan(lat)
            idsByLng = self.getLngHigherThan(lng)
        elif area == 3:
            idsByLat = self.getLatLowerThan(lat)
            idsByLng = self.getLngLowerThan(lng)
        elif area == 4:
            idsByLat = self.getLatLowerThan(lat)
            idsByLng = self.getLngHigherThan(lng)
        # get intersection
        return list(set(idsByLat).intersection(set(idsByLng)))

    def getLatHigherThan(self, lat):
        return [self.latIds[x] for x in self.lats if x >= lat]

    def getLatLowerThan(self, lat):
        return [self.latIds[x] for x in self.lats if x <= lat]

    def getLngHigherThan(self, lng):
        return [self.lngIds[x] for x in self.lngs if x >= lng]

    def getLngLowerThan(self, lng):
        return [self.lngIds[x] for x in self.lngs if x <= lng]



# ---------------------
# Independent Functions
# ---------------------

def findDestinationBBox(trip, tolerance=0.01):
    latTol = tolerance
    lngTol = tolerance
    lastP = trip.destination
    lat = lastP.lat
    lng = lastP.lng
    # voting area
    area = [0,0,0,0]
    oppIdx = [4,3,2,1]
    for curP in trip.route[:-1]:
        if curP.lat < lat and curP.lng < lng:
            area[0] += 1
        elif curP.lat < lat and curP.lng > lng:
            area[1] += 1
        elif curP.lat > lat and curP.lng < lng:
            area[2] += 1
        elif curP.lat > lat and curP.lng > lng:
            area[3] += 1
    # find maximum area and than pick the opposite one
    maxIdx = [i for i in range(0,len(area)) if area[i]==max(area)][0]
    idx = oppIdx[maxIdx]
    # add tolerance
    if tolerance:
        if idx == 1:
            lat -= latTol
            lng += lngTol
        if idx == 2:
            lat -= latTol
            lng -= lngTol
        if idx == 3:
            lat += latTol
            lng += lngTol
        if idx == 4:
            lat += latTol
            lng -= lngTol
    return idx, lat, lng