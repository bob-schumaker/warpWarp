"""
Purpose: move the selected ship. 
"""


from hexgrid import *
from tkinter import *
from xbm import TileContent
import dataModel
from mapUtil import *
from ijk import *
from cmds import warpWarCmds
import math

# PURPOSE:
# RETURNS:
def createMoveGraph(tkRoot, game, hexMap, shipName):
    ship = dataModel.findShip(game, shipName)
    startI, startJ, startK = XYtoIJK(ship['location']['x'], ship['location']['y'])
    movesLeft = ship['moves']['cur']

    hiliteColor = 'Green'
    player = dataModel.playerTableGet(game, tkRoot.cfg.Profile.plid())
    if (player):
        hiliteColor = player['color']

    for i in range(-movesLeft, movesLeft + 1):
        for j in range(-movesLeft, movesLeft + 1):
            for k in range(-movesLeft, movesLeft + 1):
                if i+j+k==0:
                    x,y = IJKtoXY(startI + i, startJ + j, startK + k)
                    hexMap.setBorders(x, y, hiliteColor)

    if (movesLeft > 0):
        #if they go to one of these locations, it only costs one
        warpEnds = dataModel.getWarpLineEnd(game,
                                            ship['location']['x'],
                                            ship['location']['y'])
        for warpEnd in warpEnds:
            hexMap.setBorders(warpEnd[0], warpEnd[1], hiliteColor)
        private = [tkRoot, shipName, tkRoot.hexMap.getLeftPrivateCallBack(), warpEnds]
        hexMap.setLeftPrivateCallBack(moveOnClick, private)

# PURPOSE:
# RETURNS:
def moveOnClick(private, x, y):
    tkRoot = private[0]
    shipName = private[1]
    original = private[2]
    warpEnds = private[3]
    #write the ship where it should be.
    print("Left Click to Move", shipName)
    ship = dataModel.findShip(tkRoot.game, shipName)

    #can we move there?
    moveLeft = ship['moves']['cur']
    cur_x = ship['location']['x']
    cur_y = ship['location']['y']

    si,sj,sk = XYtoIJK(x,y)
    fi,fj,fk = XYtoIJK(cur_x,cur_y)
    delta = int((abs(si-fi) + abs(sj-fj) + abs(sk-fk)) / 2)
    if [x,y] in warpEnds:
        delta = 1
    if (delta <= moveLeft):
        ship['location']['x'] = x
        ship['location']['y'] = y
        #find the ijk stuff for decrementing the right number of moves
        ship['moves']['cur'] = ship['moves']['cur'] - delta

        # Restore the old call back
        tkRoot.hexMap.setLeftPrivateCallBack(original[0], original[1])

        # Send the move command to the server
        # We could also Queue up all the move commands
        # and play them out to the server later.
        # That would permit the user to change their
        # mind about a move and cancel it before it is
        # permanent
        if (tkRoot.hCon is not None):
            sendJson = warpWarCmds().moveShip(tkRoot.cfg.Profile.plid(), shipName, x, y)
            tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def retreatOnClick(private, x, y):
    tkRoot   = private[0]
    shipName = private[1]
    original = private[2]
    warpEnds = private[3] # should retreat allow along warp lines?

    #write the ship where it should be.

    print("Left click to retreat", shipName, "to", x, y)
    ship = dataModel.findShip(tkRoot.game, shipName)

    #can we move there?
    moveLeft = 1
    cur_x = ship['location']['x']
    cur_y = ship['location']['y']

    # How far away is the mouse click?
    si,sj,sk = XYtoIJK(x,y)
    fi,fj,fk = XYtoIJK(cur_x,cur_y)
    delta = int((abs(si-fi) + abs(sj-fj) + abs(sk-fk)) / 2)
    if [x,y] in warpEnds:
        delta = 1

    if (delta <= moveLeft):

        # ok, it's less than 1 away but is it legal for me to move there
        # during a retreat?
        enemyPresent = False
        objList = dataModel.findObjectsAt(tkRoot.game, x, y)
        for obj in objList:
           if (obj['owner'] != tkRoot.cfg.Profile.plid()):
                enemyPresent = True

        if (not enemyPresent):
            ship['location']['x'] = x
            ship['location']['y'] = y

            # Restore the old call back
            tkRoot.hexMap.setLeftPrivateCallBack(original[0], original[1])

            # Send the move command to the server
            # We could also Queue up all the move commands
            # and play them out to the server later.
            # That would permit the user to change their
            # mind about a move and cancel it before it is
            # permanent
            if (tkRoot.hCon is not None):
                sendJson = warpWarCmds().acceptRetreat(tkRoot.cfg.Profile.plid(),
                                                       shipName, x, y)
                tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def createRetreatGraph(tkRoot, game, hexMap, shipName):
    ship = dataModel.findShip(game, shipName)
    startI, startJ, startK = XYtoIJK(ship['location']['x'],
                                     ship['location']['y'])
    # can only move one on retreat
    movesLeft = 1

    hiliteColor = 'Green'
    player = dataModel.playerTableGet(game, tkRoot.cfg.Profile.plid())
    if (player):
        hiliteColor = player['color']

    for i in range(-movesLeft, movesLeft + 1):
        for j in range(-movesLeft, movesLeft + 1):
            for k in range(-movesLeft, movesLeft + 1):
                if i+j+k==0:
                    x,y = IJKtoXY(startI + i, startJ + j, startK + k)

                    # Only if there is no enemy or uncontrolled space here
                    enemyPresent = False
                    objList = dataModel.findObjectsAt(game, x, y)
                    for obj in objList:
                       if (obj['owner'] != tkRoot.cfg.Profile.plid()):
                            enemyPresent = True

                    if (not enemyPresent):
                        # Nobody there. Free to move
                        hexMap.setBorders(x, y, hiliteColor)

    warpEnds = []
    private = [tkRoot,
               shipName,
               tkRoot.hexMap.getLeftPrivateCallBack(),
               warpEnds]
    hexMap.setLeftPrivateCallBack(retreatOnClick, private)
