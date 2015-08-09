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

# ---------------- 
# Loading Data
# ---------------- 
class GridObj:

    def __init__(self):
        self.cell_cellId = {} # lo_lat -> hi_lat -> lo_lng -> hi_lng -> id
        self.cellId_trainId = {} # cell_id -> [trainId_1, trainId_2, trainId_3, ..]
        self.lastId = -1


    # ------------------------
    # Parsing the train routes
    # ------------------------
    def loadTrainRoutes(self, trips):
        for tid in trips:
            route = trips[tid].route
            routeCells = self.getRouteCells(route)
            # store
            for rCell in routeCells:
                cellId = self.storeCellAndGetId(rCell)
                rCell.id = cellId
                if not self.cellId_trainId.has_key(cellId):
                    self.cellId_trainId[cellId] = []
                self.cellId_trainId[cellId].append( tid )


    def storeCellAndGetId(self, cell):
        lo_lat = cell.lo_lat
        hi_lat = cell.hi_lat
        lo_lng = cell.lo_lng
        hi_lng = cell.hi_lng
        #
        if not self.cell_cellId.has_key(lo_lat):
            self.cell_cellId[lo_lat] = {}
        if not self.cell_cellId[lo_lat].has_key(hi_lat):  
            self.cell_cellId[lo_lat][hi_lat] = {}
        if not self.cell_cellId[lo_lat][hi_lat].has_key(lo_lng):
            self.cell_cellId[lo_lat][hi_lat][lo_lng] = {}
        if not self.cell_cellId[lo_lat][hi_lat][lo_lng].has_key(hi_lng):
            self.lastId += 1
            self.cell_cellId[lo_lat][hi_lat][lo_lng][hi_lng] = self.lastId
        # 
        return self.cell_cellId[lo_lat][hi_lat][lo_lng][hi_lng]

    def noCells(self):
        return len(self.cellId_trainId)


    """ Given a route, compute all the cells that it has visited. """
    def getRouteCells(self, route):
        routeCells = []
        routeCellCnt = {}
        for P in route:
            pCell = CellsObj(P)
            routeCells.append( pCell )
        #
        return routeCells


    # -----------------------
    # Processing a test route
    # -----------------------

    """ Given a route, find the candidates that pass from the same (m)cells """
    def getGridCandidates(self, route, last_cells=3):
        routeCells = self.getRouteCellIds(route)
        candidates = set()
        # edge cases
        if len(routeCells) == 1:
            return candidates
        elif len(routeCells) < last_cells:
            last_cells = 2
        # get candidates for the last "last_cells"
        for i in range(1,last_cells+1):
            cellId = routeCells[-i]
            if self.cellId_trainId.has_key( cellId ):
                if len(candidates) == 0:
                    candidates = set(self.cellId_trainId[ cellId ])
                else:
                    candidates.intersection(set(self.cellId_trainId[ cellId ]))
        # remove duplicates
        return list(candidates)


    """ Given a route, compute all the cells that it has visited. """
    def getRouteCellIds(self, route):
        routeCells = []
        routeCellCnt = {}
        for P in route:
            pCell = CellsObj(P)
            # get cellId
            pCellId = self.getCellId( pCell )
            #
            routeCells.append( pCellId )
            # keep track of the no. of points the route has for each cell
            # if not routeCellCnt.has_key(pCellId):
            #     routeCellCnt[pCellId] = 0
            # routeCellCnt[pCellId] += 1
        #
        return routeCells
    

    """ Given a cell, find it in the train grid and return the Id """
    def getCellId(self, cell):
        lo_lat = cell.lo_lat
        hi_lat = cell.hi_lat
        lo_lng = cell.lo_lng
        hi_lng = cell.hi_lng
        if self.cell_cellId.has_key(lo_lat):
            if self.cell_cellId[lo_lat].has_key(hi_lat):
                if self.cell_cellId[lo_lat][hi_lat].has_key(lo_lng):
                    if self.cell_cellId[lo_lat][hi_lat][lo_lng].has_key(hi_lng):
                        return self.cell_cellId[lo_lat][hi_lat][lo_lng][hi_lng]
        # if no cell found
        self.lastId += 1
        return self.lastId




# -------------
# Cell Data
# -------------
class CellsObj:

    def __init__(self, point):
        self.borders = self.computeCells(point)
        self.id = -1
        self.lo_lat = self.borders[0]
        self.hi_lat = self.borders[1]
        self.lo_lng = self.borders[2]
        self.hi_lng = self.borders[3]

    """ Given a route, compute the cells that have been visited """
    def computeCells(self, P):
        # compute cell verteces
        lo_lat = int(P.lat*100)/100.
        hi_lat = float('%.2f'% (lo_lat+0.01)) if lo_lat >= 0 else float('%.2f'% (lo_lat-0.01))
        lo_lng = int(P.lng*100)/100.
        hi_lng = float('%.2f'% (lo_lng+0.01)) if lo_lng >= 0 else float('%.2f'% (lo_lng-0.01))
        return [lo_lat, hi_lat, lo_lng, hi_lng]
