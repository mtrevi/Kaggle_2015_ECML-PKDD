# -*- coding: utf-8 -*-
"""
Distance Metrics contains a collection of function to compute the distance between given points.
__source__ : 
__author__ : Michele Trevisiol @trevi
"""

import sys
import simplejson, urllib
from haversine import haversine


""" Compute the Haversine Distance between two points
"""
def haversineDist(p1,p2):
    coo1 = [p1.lat, p1.lng]
    coo2 = [p2.lat, p2.lng]
    return haversine(coo1, coo2)

""" TODO: CHECK IT OUT (didn't evaluate it yet) !!!
    __source__ : https://developers.google.com/maps/documentation/distancematrix/intro
"""
def googleMapsDist(p1,p2):
    orig_coord = p1.lat, p1.lng
    dest_coord = p2.lat, p2.lng
    url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(orig_coord),str(dest_coord))
    result= simplejson.load(urllib.urlopen(url))
    driving_time = result['rows'][0]['elements'][0]['duration']['value']


""" @p1: first point in WGS84 format
    @p2: second point in WGS84 format
"""
def getGPSDistance(p1, p2, func='haversine'):
    if func == 'haversine':
        return haversineDist(p1,p2)
    elif func == 'googlemaps':
        return googleMapsDist(p1,p2)
