# -*- coding: utf-8 -*-
"""
Trip object contains all the information of an individual trip. 
__source__ : 
__author__ : Michele Trevisiol @trevi
"""

import sys
import csv
from ast import literal_eval
from GPSPoint import *

class TripObj:

    def __init__(self, b, sep=','):
        self.id = b[0]
        self.callType = self.convertChar2Int(b[1], 'call_type') # A:1, B:2, C:3
        self.originCall = self.parsingInt(b[2])
        self.originStandId = self.parsingInt(b[3]) # refers to meta
        self.taxiId = int(b[4])
        self.ts = long(b[5])
        self.dayType = self.convertChar2Int(b[6], 'day_type') # A:1, B:2, C:3
        self.missingData = bool(b[7])
        self.route = self.getListOfPoints(b[8])
        if len(self.route) > 0:
            self.destination = self.route[-1]
        else:
            self.destination = None

    # ---------------- 
    # Loading Fields
    # ---------------- 

    def convertChar2Int(self, val, field):
        if val == 'A':
            return 1
        elif val == 'B':
            return 2
        elif val == 'C':
            return 3
        else:
            print >> sys.stderr, 'Error parsing %s (%s)'%(field,val)

    def parsingInt(self, val):
        try:
            return int(val)
        except:
            return -1

    def getListOfPoints(self, string):
        ll = list(literal_eval(string.strip()))
        l_out = []
        for val in ll:
            l_out.append( GPSPoint(val,order='lnglat') )
        return l_out

    # ---------------- 
    # Getting Info
    # ---------------- 

    def printRoute(self):
        for p in self.route:
            print '(%f,%f)' %(p.lat,p.lng), 
        print ''
