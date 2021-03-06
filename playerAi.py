# AI Player for WarpWar
#
# This is a brain dead AI. It connects to the
# WarpWar server and holds the place of a player
# and sends and receives messages
#
# Written with Python 3.4.2
#

# Imports
import socket
import threading
import queue as Q
import gameserver
import json
import time
import dataModel
import ijk
import math
from cmds import warpWarCmds
from client import comThrd

# thread for the player
class playerAiThrd(threading.Thread):

    # PURPOSE: Called for class construction
    # RETURNS: none
    def __init__(self, name, ipAddr, port, startingBases):
        self.playerName = name
        self.plid = 123
        self.nameCnt = 0
        self.startingBases = startingBases
        self.color = 'Green'
        self.ipAddr = ipAddr
        self.port = port
        self.threadContinue = True
        self.rcvQ = Q.Queue()
        threading.Thread.__init__(self, name="playerAiThrd")
        self.start()

    # PURPOSE: For anyone to kill the thread
    #   called by external parties
    # RETURNS: none
    def quit(self):
        print("playerAi: quiting")
        self.rcvQ.put("quit")

    # PURPOSE: Simple ping to the server to read game state
    # RETURNS: none
    def ping(self):
        sendJson = warpWarCmds().ping(self.plid)
        self.hCon.sendCmd(sendJson)

    # PURPOSE: 
    # RETURNS: none
    def newPlayer(self):
        print("playerAi: newPlayer")
        sendJson = warpWarCmds().newPlayer(self.plid,
                                           self.playerName,
                                           self.startingBases,
                                           self.color)
        self.hCon.sendCmd(sendJson)

    # PURPOSE: 
    # RETURNS: none
    def leave(self):
        print("playerAi: leaveGame")
        sendJson = warpWarCmds().playerLeave(self.plid)
        self.hCon.sendCmd(sendJson)

    # PURPOSE: 
    # RETURNS: none
    def ready(self):
        print("playerAi: ready")
        sendJson = warpWarCmds().ready(self.plid)
        self.hCon.sendCmd(sendJson)

    # PURPOSE: Build a "random ship"
    #          Doesn't need to be in class
    # RETURNS: none
    def createShip(self, BP, x, y):
        self.nameCnt += 1
        name = "W" + str(self.nameCnt)
        PD = 5
        WG = True
        B = 3
        S = 3
        T = 2
        M = 2
        SR = 0
        H = 0

        moves = math.ceil(int(PD/2))
        ship =  {
             'name': name,
             'type': "ship",
             'location': {'x':x, 'y':y},
             'image':"ship1.png",
             'owner': self.plid,
             'techLevel': 1,
             'damage': 0,
             'moves': {'max': moves, 'cur': moves },
             'PD': {'max': PD, 'cur': PD },       # PowerDrive
             'WG': {'max': WG, 'cur': WG }, # Warp Generator
             'B':  {'max':B, 'cur':B },       # Beams
             'S':  {'max':S, 'cur':S },       # Screens (Shields)
             'E':  {'max':0, 'cur':0 },       # Electronic Counter Measures (New)
             'T':  {'max':T, 'cur':T },       # Tubes
             'M':  {'max':M * 3, 'cur':M * 3 },       # Missiles
             'A':  {'max':0, 'cur':0 },       # Armor (New)
             'C':  {'max':0, 'cur':0 },       # Cannons (New)
             'SH': {'max':0 * 6, 'cur':0 * 6 },       # Shells (New)
             'SR': {'max':SR, 'cur':SR },       # System Ship Racks
             'H':  {'max':H, 'cur':H },       # Holds (New)
             'Hauled':0,
             'R': {'max':0, 'cur':0 },       # Repair Bays (New)
             'visibility':[ {'player':self.plid,  'percent':100}],
             'carried_ships' :[],
            }
        return ship

    # PURPOSE: 
    # RETURNS: none
    def moveShip(self, ship, game):
        # Where am I
        curLoc = ship['location']
        # How far can I go
        curRange = ship['moves']['cur']
        print(ship['name'], "at", curLoc, "range", curRange)
        # Where *should* I go?
        #   Pick up BP
        #   Drop off BP
        #   Conquer planet
        #   Attack enemy ship
        #   Pick up System Ship
        #   Drop off System Ship
        # I'd like to create a random objective and store it with
        # The ship. For now just conquer and attack.

        # Find the plid of the other player.
        # If there are more than one other player
        # only gets the first one
        otherPlid = None
        for player in game['playerList'] :
            if (player['plid'] != self.plid):
                otherPlid = player['plid']

        print("otherPlid", otherPlid)
        # Find the nearest thing that I don't own.
        unOwnedList = dataModel.getOwnedList(game, None)
        otherPlayerList = dataModel.getOwnedList(game, otherPlid)

        for obj in unOwnedList:
            # Find the closest thing.
            si,sj,sk = ijk.XYtoIJK(curLoc['x'], curLoc['y'])
            fi,fj,fk = ijk.XYtoIJK(obj['location']['x'], obj['location']['y'])
            delta = int((abs(si-fi) + abs(sj-fj) + abs(sk-fk)) / 2)
            print("to obj", obj['name'], " delta ", delta)

    # PURPOSE: 
    # RETURNS: none
    def selectDamageShip(self, ship):
        assert(ship)

        damLeft = ship['damage']
        print("playerAi:", ship['name'], " taking ", damLeft, " damage ")

        # Drain Holds and System Racks
        changeCheck = 0
        while ((damLeft > 0) and damLeft != changeCheck):
            changeCheck = damLeft
            if (damLeft > 0):
                if (ship['H']['cur'] > 0):
                    ship['H']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['SR']['cur'] > 0):
                    ship['SR']['cur'] -= 1
                    damLeft -= 1

        changeCheck = 0
        while ((damLeft > 0) and damLeft != changeCheck):
            changeCheck = damLeft
            if (damLeft > 0):
                if (ship['T']['cur'] > 2):
                    ship['T']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['S']['cur'] > 2):
                    ship['S']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['B']['cur'] > 2):
                    ship['B']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['PD']['cur'] > 4):
                    ship['PD']['cur'] -= 1
                    damLeft -= 1

        changeCheck = 0
        while ((damLeft > 0) and damLeft != changeCheck):
            changeCheck = damLeft
            if (damLeft > 0):
                if (ship['T']['cur'] > 1):
                    ship['T']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['S']['cur'] > 1):
                    ship['S']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['B']['cur'] > 1):
                    ship['B']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['PD']['cur'] > 2):
                    ship['PD']['cur'] -= 1
                    damLeft -= 1

        changeCheck = 0
        while ((damLeft > 0) and damLeft != changeCheck):
            changeCheck = damLeft
            if (damLeft > 0):
                if (ship['T']['cur'] > 0):
                    ship['T']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['S']['cur'] > 0):
                    ship['S']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['B']['cur'] > 0):
                    ship['B']['cur'] -= 1
                    damLeft -= 1
            if (damLeft > 0):
                if (ship['PD']['cur'] > 0):
                    ship['PD']['cur'] -= 1
                    damLeft -= 1

        # This better be zero ... or the ship explodes
        ship['damage'] = damLeft

    # PURPOSE: 
    # RETURNS: none
    def buildThings(self, game):
        # Loop through every base I own
        baseList = dataModel.getOwnedListOfType(game, self.plid, 'starBaseList')
        for base in baseList:
            # Take the points at that base and build a ship there
            print("playerAI: build something at ",
                  base['name'],
                  " for ", base['BP']['cur'])
            ship = self.createShip(base['BP']['cur'], base['location']['x'],
                                                      base['location']['y'])
            if ship:
                sendJson = warpWarCmds().buildShip(self.plid,
                                                   ship,
                                                   base['name'])
                self.hCon.sendCmd(sendJson)

    # PURPOSE: 
    # RETURNS: none
    def moveThings(self, game):
        # Loop through every ship I own
        shipList = dataModel.getOwnedListOfType(game, self.plid, 'shipList')
        for ship in shipList:
            print("playerAI: move ship", ship['name'], " at ",
                   ship['location']['x'], ", ", ship['location']['y'])
            self.moveShip(ship, game)
 


    # PURPOSE: 
    # RETURNS: none
    def combatOrders(self):
        print("playerAi: combatOrders (nothing right now)")
        #sendJson = warpWarCmds().combatOrders(self.plid, tkRoot.battleOrders)
        #self.hCon.sendCmd(sendJson)

    # PURPOSE: 
    # RETURNS: none
    def selectDamageAll(self, game):
        print("playerAi: select damage")
        # Find ships with damage
        for ship in game['objects']['shipList']:
            if (ship['owner'] == self.plid) and (ship['damage'] > 0):
                self.selectDamageShip(ship)
                sendJson = warpWarCmds().acceptDamage(self.plid, ship)
                self.hCon.sendCmd(sendJson)

    # PURPOSE: This is called in the context of the client socket
    #   receiving thread
    #   Put that data in the PlayerAI Q so the main thread can read it
    # RETURNS: none
    def newDataForGame(self, data):
        #print("playerAI: newDataForGame")
        jsonStr = data.decode()
        self.rcvQ.put(jsonStr)

    # PURPOSE: automatically called by base thread class, right?
    #   Waits for clients to send us requests.
    # RETURNS: none
    def run(self):

        gamePhase = None
        playerPhase = None

        self.hCon = comThrd(self.ipAddr, self.port, "playerAI")
        self.hCon.setCallback(lambda data: self.newDataForGame(data))

        while (self.threadContinue):

            # The input Q should just have a bunch
            # of updates from the server ... the "game"
            try:
                resp = self.rcvQ.get(True, 5)
            except Q.Empty:
                resp = "{}"

            if (resp == "quit"):
                self.threadContinue = False
                continue

            game = json.loads(resp)

            if ( not game ):
                # Ping
                self.ping()
                time.sleep(1)
                continue

            playerMe = dataModel.playerTableGet(game, self.plid)
            if (playerMe is None):
                playerMe = {'phase':None}

            # If the game state hasn't changed, skip and try again.
            if ( (gamePhase == game['state']['phase']) and
                 (playerPhase == playerMe['phase']) ):
                # Ping
                self.ping()
                time.sleep(1)
                continue

            gamePhase   = game['state']['phase']
            playerPhase = playerMe['phase']

            # Do something with that state
            print("playerAi:GamePhase ", gamePhase, " PlayerPhase ", playerPhase)
            if (gamePhase == "creating"):
                if ( (playerPhase is None) or (playerPhase == "nil")):
                    self.newPlayer()
            elif (gamePhase == "build"):
                if (playerPhase == "build"):
                    self.buildThings(game)
                    self.ready()
            elif (gamePhase == "move"):
                if (playerPhase == "move"):
                    self.moveThings(game)
                    self.ready()
            elif (gamePhase == "combat"):
                if (playerPhase == "combat"):
                    self.combatOrders()
                    self.ready()
            elif (gamePhase == "damageselection"):
                if (playerPhase == "damageselection"):
                    self.selectDamageAll(game)
                    self.ready()
            elif (gamePhase == "quiting"):
                self.leave()
                self.quit()
            else:
                # Ping
                self.ping()
                time.sleep(1)

        # If AI player is quiting AI player should politely leave game
        self.leave()

        self.hCon.quitCmd()
        self.hCon.join()

        print("playerAi:run: exiting")
