#
# Make the construction of json commands easier to use.
#

import sys
sys.path.append("/home/ahw/views/warpWar/test")

import json

# A class to create json commnds
# Does this really need to be a class? It seems like just using the namespace
# would be good enough?
class warpWarCmds():

    # PURPOSE: Called for class construction
    # RETURNS: none
    def __init__(self):
        # print("create Cmd ... thingy")
        pass

    # PURPOSE: test for server connectivity
    # RETURNS: string with json
    def ping(self, plid):
        cmd  = { 'cmd' : {'cmd': "ping", 'plid': plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create a new game string
    #          (moves to creating phase)
    # RETURNS: string with json
    def newGame(self, plid, name):
        cmd  = { 'cmd' : {'cmd': "newgame", 'plid':plid, 'name': name} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: join an existing game with player name
    #          "gameName" is probably ignored right now
    # RETURNS: string with json
    def join(self, plid, gameName, playerName):
        cmd  = { 'cmd' : {'cmd': "join", 'plid':plid,
                          'game': gameName, 'player': playerName} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the new player string
    #    DUPLICATE TODO FIXME XXX 
    # RETURNS: string with json
    def newPlayer(self, plid, name):
        cmd  = { 'cmd' : {'cmd': "newplayer", 'plid':plid, 'name': name} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Generic ready command.
    #          Given player is ready for next phase
    # RETURNS: string with json
    def ready(self, plid, player):
        cmd  = { 'cmd' : {'cmd': "ready", 'plid':plid, 'name': player} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Start the game
    #          (moves to build phase)
    # RETURNS: string with json
    def start(self, plid):
        cmd  = { 'cmd' : {'cmd': "start", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the build ship string
    #       TODO    This is going to have many arguments!
    # RETURNS: string with json
    def buildShip(self, plid, ship, base):
        cmd  = { 'cmd' : {'cmd': "buildship", 'plid':plid, 'ship': ship, 'base': base} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the move ship string
    # RETURNS: string with json
    def moveShip(self, plid, name, x, y):
        cmd  = { 'cmd' : {'cmd':"moveship", 'plid':plid, 'name':name, 'x':x, 'y':y} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the endmove string
    #    FIXME TODO -- duplicate of ready?
    # RETURNS: string with json
    def endMove(self, plid, name, x, y):
        cmd  = { 'cmd' : {'cmd':"endmove", 'plid':plid, 'player':name} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the combat orders string
    #       TODO    This is going to have many arguments!
    #       TODO    For all involved ships?
    # RETURNS: string with json
    def combatOrders(self, plid):
        cmd  = { 'cmd' : {'cmd': "combatorders", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the XXX string
    #       TODO    This is going to have many arguments!
    #       TODO    For all involved ships?
    # Even if you received NO damage you should send this
    # command. It will be a trigger to know a player is done
    # with a battle and ready for the next one.
    # RETURNS: string with json
    def acceptDamage(self, plid):
        cmd  = { 'cmd' : {'cmd': "acceptdamage", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the quit string
    # RETURNS: string with json
    def quitGame(self, plid):
        cmd  = { 'cmd' : {'cmd': "quit", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

# The remaining functions might not be needed

    # PURPOSE: Create the XXX string
    #    TODO This is like quiting
    # RETURNS: string with json
    def playerLeave(self, plid):
        cmd  = { 'cmd' : {'cmd': "playerleave", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the save string
    # RETURNS: string with json
    def saveGame(self, plid):
        cmd  = { 'cmd' : {'cmd': "savegame", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the XXX string
    # RETURNS: string with json
    def restoreGame(self, plid, game):
        cmd  = { 'cmd' : {'cmd': "restoregame", 'plid':plid, 'game' : game}}
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the XXX string
    # RETURNS: string with json
    def listGames(self, plid):
        cmd  = { 'cmd' : {'cmd': "listgames", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr

    # PURPOSE: Create the XXX string
    # RETURNS: string with json
    def loadGame(self, plid):
        cmd  = { 'cmd' : {'cmd': "loadgame", 'plid':plid} }
        jsonStr = json.dumps(cmd, ensure_ascii=False)
        return jsonStr
