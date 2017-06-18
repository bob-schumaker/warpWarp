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
from client import comThrd
import queue as Q
import gameserver
import json
from cmds import warpWarCmds
from dataModel import *

# thread for the player
class playerAiThrd(threading.Thread):

    # PURPOSE: Called for class construction
    # RETURNS: none
    def __init__(self, name, ipAddr, port):
        self.playerName = name
        self.ipAddr = ipAddr
        self.port = port
        self.threadContinue = True
        self.client = None
        threading.Thread.__init__(self, name="playerAiThrd")
        self.start()

    # PURPOSE: For anyone to kill the thread
    #   called by external parties
    # RETURNS: none
    def quit(self):
        print("playerAi: quiting")
        self.threadContinue = False

    # PURPOSE: Simple ping to the server to read game state
    # RETURNS: game object
    def ping(self):
        sendJson = warpWarCmds().ping(self.playerName)
        self.hCon.sendCmd(sendJson)
        resp = self.hCon.waitFor(5)
        game = json.loads(resp)
        return game

    # PURPOSE: 
    # RETURNS: game object
    def newPlayer(self, name):
        print("playerAi: newPlayer")
        sendJson = warpWarCmds().newPlayer(self.playerName, name)
        self.hCon.sendCmd(sendJson)
        resp = self.hCon.waitFor(5)
        game = json.loads(resp)
        print("playerAi:RESP:", len(resp))
        return game

    # PURPOSE: 
    # RETURNS: game object
    def ready(self, name):
        print("playerAi: ready")
        sendJson = warpWarCmds().ready(self.playerName, name)
        self.hCon.sendCmd(sendJson)
        resp = self.hCon.waitFor(5)
        game = json.loads(resp)
        print("playerAi:RESP:", len(resp))
        return game

    # PURPOSE: automatically called by base thread class, right?
    #   Waits for clients to send us requests.
    # RETURNS: none
    def run(self):

        gamePhase = None
        playerPhase = None

        self.hCon = comThrd(self.ipAddr, self.port)

        while (self.threadContinue):
            # Ping
            game = self.ping()

            playerMe = playerTableGet(game, self.playerName)
            if (playerMe is None):
                playerMe = {'phase':None}

            # What is the current game state and player state?
            if ( (gamePhase == game['state']['phase']) and
                 (playerPhase == playerMe['phase']) ):
                 continue

            gamePhase   = game['state']['phase']
            playerPhase = playerMe['phase']

            # Do something with that state
            print("playerAi:GP ", gamePhase, " PP ", playerPhase)
            if (gamePhase == "creating"):
                if ( (playerPhase is None) or (playerPhase == "nil")):
                    self.newPlayer(self.playerName)
                elif (playerPhase == "creating"):
                    self.ready(self.playerName)
            elif (gamePhase == "build"):
                if (playerPhase == "build"):
                    self.ready(self.playerName)
            elif (gamePhase == "move"):
                if (playerPhase == "move"):
                    self.ready(self.playerName)

        self.hCon.quitCmd()

        print("playerAi:run: exiting")