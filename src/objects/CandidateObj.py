# -*- coding: utf-8 -*-
""" 
__author__ : Michele Trevisiol @trevi
__description__ : This is the class of the candidate destination that is returned within the framework.
"""

import sys

class CandidateObj:

    def __init__(self):
        self.score = -1
        self.wrongDirection = -1
        self.higherDistance = -1
        self.noPj = -1
        self.noPi = -1
        self.commPoints = -1
        # using LR
        self.slope = -1
        # using avg of last distances
        self.avgMagnitude = -1

    """ Convert WGS84 in meters
    """
    def serialize(self):
        output = 'slope: %.3f, wDir: %.3f, hDist: %.3f, avgMag: %.3f, cPoints: %.3f, noPj: %d, noPi: %d' \
        %(self.slope,self.wrongDirection,self.higherDistance,self.avgMagnitude,self.commPoints, self.noPj, self.noPi)
        # 'commPoints: %.3f(%.3f)' %(self.commPoints),
        return output