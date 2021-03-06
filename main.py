# Main program for WarpWar
# More stuff will go here someday
# Right now there is no client/server
#
# Written with Python 3.4.2
#

# imports
from hexgrid import *
from tkinter import *
from tkinter import filedialog
from dataModel import *
from hexinfo import *
from build import *
from move import *
from loadShip import *
from loadCargo import *
from combat import *
from mapUtil import *
from connect import *
from damage import *
from cmds import warpWarCmds
from ConfigHandler import ConfigHandler
import json
import getpass
import math

# Panes that can be put in the pane window
import histpane
import hexpane

# PURPOSE: Timer call back every second to check if the mouse has moved.
#          If it hasn't moved create a tool tip of info for the given location
#          Perhaps more colors?
# RETURNS:
def tooltip(tkRoot):
    x,y = tkRoot.hexMap.getCurrentPoint()
    if ( (x != tkRoot.tooltipX) or (y != tkRoot.tooltipY) ):
        tkRoot.tooltipX = x
        tkRoot.tooltipY = y
        tkRoot.tooltipCount = 0
        if (tkRoot.tooltip):
            tkRoot.tooltip.destroy()
            tkRoot.tooltip = None
        
    if ((x > 0) and (y > 0)):
        tkRoot.tooltipCount += 1
        if (tkRoot.tooltipCount == 2):
            x,y = tkRoot.hexMap.getHexForPix(x, y)
            if ((x > 0) and (y > 0)):
                #print("tooltip trigger", x, y)
                text = ""
                objs = findObjectsAt(tkRoot.game, x, y)
                for obj in objs:
                    if text:
                        text += "\n"
                    text += obj['type'] + ":" + obj['name']

                if not text:
                    text = "The vast emptiness of space"
            
                # creates a toplevel window
                tkRoot.tooltip = tk.Toplevel(tkRoot)
                # Leaves only the label and removes the app window
                tkRoot.tooltip.wm_overrideredirect(True)
                x,y = tkRoot.winfo_pointerxy()
                label = tk.Label(tkRoot.tooltip, text=text, justify='left',
                               background="#ffffff", relief='solid', borderwidth=1,
                               wraplength = 100)
                height = label.winfo_reqheight()
                tkRoot.tooltip.wm_geometry("+%d+%d" % (x, y-height))
                label.pack(ipadx=1)
                tkRoot.hexInfoFrame.update(objs)



    tkRoot.after(10, lambda :tooltip(tkRoot))

# PURPOSE: Button handler. The Quit button
#          call this when "Quit" button clicked
# RETURNS: I don't know.
def exitProgram(tkRoot):
    print("quitMain")

    if (tkRoot.hCon):
        sendJson = warpWarCmds().playerLeave(tkRoot.plid)
        tkRoot.hCon.sendCmd(sendJson)
        sendJson = warpWarCmds().quitGame(tkRoot.plid)
        tkRoot.hCon.sendCmd(sendJson)
        tkRoot.hCon.quitCmd()

    if (tkRoot.hPlayerAi):
        tkRoot.hPlayerAi.quit()

    # We should wait for the playerLeave and quit command
    # to finish, right?
    tkRoot.destroy()
    tkRoot.quit()

# I don't like these. They don't seem very objecty
# Perhaps each of them should be a class?
def connectServer(tkRoot):
    print("main:connectServer")
    if (tkRoot.hCon is not None):
        tkRoot.hCon.quitCmd()
        tkRoot.hCon = None

    tmp = connect(tkRoot, tkRoot.cfg);
    if (tmp is not None):
        tkRoot.hCon = tmp.hCon
        tkRoot.plid = tmp.plid
        tkRoot.hPlayerAi = tmp.hPlayerAi

    if (tkRoot.hCon is not None):
        tkRoot.hCon.setCallback(lambda data: newDataForGame(tkRoot, data))
        refresh(tkRoot)

        print ("tkroot.plid: {} Name: {}".format(tkRoot.plid, dataModel.playerNameGet(tkRoot.game, tkRoot.plid)))

# PURPOSE:
# RETURNS:
def newGame(tkRoot):
    print("newGame")
    print("What does newGame event mean? Kill old game and reconnect?")
    if (tkRoot.hCon is not None):
        sendJson = warpWarCmds().newGame(tkRoot.plid, dataModel.playerNameGet(tkRoot.game, tkRoot.plid),"foo")
        print(" main sending: ", sendJson)
        tkRoot.hCon.sendCmd(sendJson)

        #sendJson = warpWarCmds().newPlayer(tkRoot.plid, dataModel(tkRoot.game, tkRoot.plid) tkRoot.playerStartBases, tkRoot.playerColor)
        #tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def sendStartMenu(tkRoot):
    print("sendStartMenu")
    tkRoot.event_generate("<<sendStart>>", when='tail')

# PURPOSE:
# RETURNS:
def sendReadyMenu(tkRoot):
    print("sendReadyMenu")
    tkRoot.event_generate("<<sendReady>>", when='tail')

# PURPOSE:
# RETURNS:
def playerJoinMenu(tkRoot):
    print("playerJoinMenu")
    print("Should launch dialog to pick")
    if (tkRoot.hCon is not None):
        sendJson = warpWarCmds().playerLeave(tkRoot.plid)
        tkRoot.hCon.sendCmd(sendJson)

        #sendJson = warpWarCmds().newPlayer(tkRoot.plid, dataModel.playerNameGet(tkRoot.game, tkRoot.plid), tkRoot.playerStartBases, tkRoot.playerColor)
        #tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def combatAtLocation(tkRoot, friendlyShips, enemyShips):
    print("combatAtLocationMenu")
    combatResult = None
    if (friendlyShips and enemyShips):
        combatResult = combat(tkRoot, friendlyShips, enemyShips)

    if (combatResult is not None):
        print (combatResult.combatOrders)

        tkRoot.battleOrders.update(combatResult.combatOrders)

# PURPOSE:
# RETURNS:
def conquestAtLocation(tkRoot, friendlyShips, nonShipList):
    print("conquestAtLocation")
    if (friendlyShips):
        ship = friendlyShips[0]
        tkRoot.battleOrders[ship['name']] = {
                                                'ship' : ship['name'],
                                                'conquer': nonShipList,
                                                'tactic': 'CONQUER'
                                            }

# PURPOSE:
# RETURNS:
def sendCombatReady(tkRoot):
    print("readyMenu")
    if (tkRoot.hCon is not None):

        if (tkRoot.battleOrders):
            sendJson = warpWarCmds().combatOrders(tkRoot.plid, tkRoot.battleOrders)
            print(" main sending: ", sendJson)
            tkRoot.hCon.sendCmd(sendJson)

        # We've sent our orders, erase them
        tkRoot.battleOrders = {}

        # Send ready because we are done with this round of combat
        sendJson = warpWarCmds().ready(tkRoot.plid)
        print(" main sending: ", sendJson)
        tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def retreatMenu(tkRoot, shipName):
    print("retreatMenu", shipName)
    if (tkRoot.hCon is not None):
        ship = findShip(tkRoot.game, shipName)
        createRetreatGraph(tkRoot, tkRoot.game, tkRoot.hexMap, shipName)

# PURPOSE:
# RETURNS:
def damageAllocationMenu(tkRoot, shipName):
    print("damageAllocationMenu", shipName)
    if (tkRoot.hCon is not None):
        ship = findShip(tkRoot.game, shipName)
        allocationResult = damageAllocation(tkRoot, ship)

        if (allocationResult is not None and allocationResult.finished):
            sendJson = warpWarCmds().acceptDamage(tkRoot.plid,
                                                  allocationResult.ship)
            print(" main sending: ", sendJson)
            tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def buildShip(tkRoot, baseName):
    print("buildMenu", baseName)
    base = findBase(tkRoot.game, baseName)
    if (base and tkRoot.hCon is not None):
        buildResult = build(tkRoot, base)

    if (buildResult is not None and buildResult.ship):
        sendJson = warpWarCmds().buildShip(tkRoot.plid, buildResult.ship, baseName)
        print(" main sending: ", sendJson)
        tkRoot.hCon.sendCmd(sendJson)

# PURPOSE: opens the load ship menu and sends the command
# RETURNS: none
def loadShip(tkRoot, ship, shipList):
    print("loadShipMenu")
    if (tkRoot.hCon is not None):
        #I don't like sending the whole tkRoot here. if you have an idea, do it.
        loadResult = loadShipMenu(tkRoot, ship, shipList)

    if (loadResult is not None and loadResult.finished):
        if loadResult.motherVar.get() == "unload":
            motherName = findMother(tkRoot.game['objects']['shipList'], loadResult.ship['name'])
            print(motherName)
            sendJson = warpWarCmds().unloadShip(tkRoot.plid, loadResult.ship['name'], motherName)
        else:
            sendJson = warpWarCmds().loadShip(tkRoot.plid, loadResult.ship['name'], loadResult.motherVar.get())
        print(" main sending: ", sendJson)
        tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def loadCargo(tkRoot, star, ship):
    print("cargoMenu")
    if (star and ship and tkRoot.hCon is not None):
        cargoResult = loadCargoMenu(tkRoot, star, ship)

    if (cargoResult is not None and cargoResult.shipment != 0):
        sendJson = warpWarCmds().loadCargo(tkRoot.plid, star['name'], ship['name'], cargoResult.shipment)
        print(" main sending: ", sendJson)
        tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def moveMenu(tkRoot, shipName):
    print("moveMenu", shipName)
    createMoveGraph(tkRoot, tkRoot.game, tkRoot.hexMap, shipName)

# PURPOSE:
# RETURNS:
def refresh(tkRoot):
    print("refresh")
    if (tkRoot.hCon is not None):
        sendJson = warpWarCmds().ping(tkRoot.plid)
        tkRoot.hCon.sendCmd(sendJson)

# PURPOSE:
# RETURNS:
def popupPlayers(tkRoot):
    if (not tkRoot.game):
        return

    popup = Menu(tkRoot, tearoff=0)
    for player in tkRoot.game['playerList']:
        popup.add_command(label = player['name'] +
                           " " + player['phase'])
        print("player",
              player['name'],
              player['phase'],
             )

    try:
        popup.post(tkRoot.winfo_pointerx(), tkRoot.winfo_pointery())
    finally:
        popup.grab_set()
        pass

# I don't like these. They don't seem very objecty

#Do we want restrictions on when this can be called?
def loadGame(tkRoot):
    print("loadGame")
    #so we need to open a file select menu, filtering for .wwr
    #then we just parse the string to our dict.
    loadFileName = filedialog.askopenfilename(title = "Select file",filetypes = (("warpWar files","*.wwr"),("all files","*.*")))
    print (loadFileName)
    loadFile = open(loadFileName, 'r')
    gameString = loadFile.read()
    loadFile.close()
    gameDict = json.loads(gameString)

    #send the game to the server.
    sendJson = warpWarCmds().restoreGame(tkRoot.plid, gameDict)
    print (sendJson)
    tkRoot.hCon.sendCmd(sendJson)

# I don't like these. They don't seem very objecty
def saveGame(game):
    print("saveGame")
    #convert to a string, the same way we send it.
    #write to a .wwr file
    saveString = json.dumps(game, ensure_ascii=False)
    saveFileName = filedialog.asksaveasfilename(title = "Select file",filetypes = (("warpWar files","*.wwr"),("all files","*.*")))
    print (saveFileName)
    saveFile = open (saveFileName, 'w')
    saveFile.write(saveString)
    saveFile.close()

# I don't like these. They don't seem very objecty
def aboutHelp():
    print("aboutHelp")

# I don't like these. They don't seem very objecty
def helpHelp():
    print("helpHelp")

# PURPOSE: Handle <<sendReady>> event
# RETURNS:
def sendReady(event, tkRoot):
    print("sendReady:", event)
    if (tkRoot.hCon is not None):
        sendJson = warpWarCmds().ready(tkRoot.plid)
        print(" main sending: ", sendJson)
        tkRoot.hCon.sendCmd(sendJson)

# PURPOSE: Handle <<sendStart>> event
# RETURNS:
def sendStart(event, tkRoot):
    print("sendStart:", event)
    if (tkRoot.hCon is not None):
        sendJson = warpWarCmds().start(tkRoot.plid)
        print(" main sending: ", sendJson)
        tkRoot.hCon.sendCmd(sendJson)

# PURPOSE: This is called in the context of the client socket receiving thread
# We shouldn't alter tkRoot.game here because that is used in the GUI thread.
# (But at the moment I do)
# RETURNS:
def newDataForGame(tkRoot, data):
    print("main.py: newDataForGame")
    jsonStr = data.decode()
    tkRoot.game = json.loads(jsonStr)
    #print(json.dumps(tkRoot.game))
    tkRoot.event_generate("<<updateWWMenu>>", when='tail')

# PURPOSE: handle <<updateWWMenu>>
# RETURNS:
def updateWWMenu(event, tkRoot):
    print("updateWWMenu:", event)

    pt = playerTableGet(tkRoot.game, tkRoot.plid)
    playerPhase = None
    if (pt):
        playerPhase = pt['phase']

    gamePhase = None

    if (tkRoot.game):
        gamePhase = tkRoot.game['state']['phase']
        for hist in tkRoot.game['history']:
            tkRoot.histFrame.set(hist['seqid'], str(hist['cmd']) + "\n")
        if ((tkRoot.game['map']['width']  != tkRoot.hexMap.grid_width) or
            (tkRoot.game['map']['height'] != tkRoot.hexMap.grid_height)
           ):
            tkRoot.hexMap.unbind("<Configure>")
            tkRoot.topPane.remove(tkRoot.hexMap)
            tkRoot.hexMap = hexMap(tkRoot.topPane, tkRoot,
                                   tkRoot.game['map']['width'],
                                   tkRoot.game['map']['height'])
            tkRoot.topPane.add(tkRoot.hexMap, stretch='always', before=tkRoot.infoPane)

            tkRoot.hexMap.bind("<Configure>", lambda event, tkRoot=tkRoot :Configure(event, tkRoot))

    phaseMenu(tkRoot, gamePhase, playerPhase)
    tkRoot.hexMap.updateMap(tkRoot.game)

# PURPOSE: popup a right click
# RETURNS: None
def buildPopUp(private, pixel_X, pixel_Y, hex_x, hex_y):
    tkRoot = private
    popup = Menu(tkRoot, tearoff=0)
    popup.add_command(label="Bases in this sector:")
    for base in tkRoot.game['objects']['starBaseList']:
        if ( (base['owner'] == tkRoot.plid) and
             (base['location']['x'] == hex_x) and
             (base['location']['y'] == hex_y)
           ):
            labelString = "'%s'    BP left: %d" % (base['name'],
                    base['BP']['cur'])
            popup.add_command(label=labelString, 
                              command=lambda baseName=base['name']:buildShip(tkRoot, baseName))

    try:
        #disable left click
        popup.post(pixel_X, pixel_Y)
    finally:
        popup.grab_set()
        pass

# PURPOSE: popup the move menu on right click
# RETURNS: None
def movePopUp(private, pixel_X, pixel_Y, hex_x, hex_y):
    # display the popup menu
    tkRoot = private
    popup = Menu(tkRoot, tearoff=0)
    popup.add_command(label="Ships in this sector:")
    for ship in tkRoot.game['objects']['shipList']:
        if ( (ship['owner'] == tkRoot.plid) and
             (ship['location']['x'] == hex_x) and
             (ship['location']['y'] == hex_y)
           ):
            if (ship['WG']['cur'] == True):
                labelString = "'%s'    Moves left: %d/%d" % (ship['name'],
                                                             ship['moves']['cur'],
                                                             math.ceil(ship['PD']['cur']/2))
                popup.add_command(label=labelString,
                          command=lambda tkRoot=tkRoot,
                                         shipName=ship['name']:
                                         moveMenu(tkRoot, shipName))
    try:
        #disable left click
        popup.post(pixel_X, pixel_Y)
    finally:
        popup.grab_set()
        pass

# PURPOSE: popup the combat menu on right click
# RETURNS: None
def combatPopUp(private, pixel_X, pixel_Y, hex_x, hex_y):
    tkRoot = private
    popup = Menu(tkRoot, tearoff=0)
    popup.add_command(label="Combat in this sector:")

    objs = findObjectsAt(tkRoot.game, hex_x, hex_y)
    friendlyShip = []
    friendlyOther = []
    enemyShip    = []
    enemyOther    = []
    for obj in objs:
        if ( (obj['owner'] == tkRoot.plid) and
             (obj['location']['x'] == hex_x) and
             (obj['location']['y'] == hex_y)
           ):
            if (obj['type'] == 'ship'):
                friendlyShip.append(obj)
            else:
                friendlyOther.append(obj)
        else:
            if (obj['type'] == 'ship'):
                enemyShip.append(obj)
            else:
                enemyOther.append(obj)

    if ( (len(friendlyShip) > 0) and (len(enemyShip) > 0) ):
        labelString = "%d Friendlies vs %d Enemies" % (len(friendlyShip), len(enemyShip))
        popup.add_command(label=labelString,
                          command=lambda friendlyShip=friendlyShip,
                          enemyShip=enemyShip:
                          combatAtLocation(tkRoot, friendlyShip, enemyShip))
    if ( (len(friendlyShip) > 0) and (len(enemyOther) > 0) ):
        tmp = 'normal'
        if (len(enemyShip) > 0):
            tmp = 'disable'
        labelString = "%d Friendlies can counquer this sector" % (len(friendlyShip))
        bases = []
        for base in enemyOther:
            bases.append(base['name'])
        popup.add_command(label=labelString,
                          state=tmp,
                          command=lambda friendlyShip=friendlyShip,
                          bases=bases:
                          conquestAtLocation(tkRoot, friendlyShip, bases))
    if ( (len(friendlyOther) > 0) and (len(enemyShip) > 0) ):
        labelString = "%d Enemies can counquer this sector" % (len(enemyShip))
        popup.add_command(label=labelString,
                          state='disable',
                          command=lambda friendlyShip=friendlyShip:
                          conquestAtLocation(tkRoot, enemyShip, 'unused'))

    try:
        #disable left click
        popup.post(pixel_X, pixel_Y)
    finally:
        popup.grab_set()
        pass

# PURPOSE: popup a right click
# RETURNS: None
def damageSelectionPopUp(private, pixel_X, pixel_Y, hex_x, hex_y):
    tkRoot = private
    popup = Menu(tkRoot, tearoff=0)
    popup.add_command(label="Damaged Ships in this sector:")

    objs = findObjectsAt(tkRoot.game, hex_x, hex_y)
    for ship in objs:
        if ( (ship['owner'] == tkRoot.plid) and
             (ship['location']['x'] == hex_x) and
             (ship['location']['y'] == hex_y) and
             (ship['type'] == 'ship') 
           ):
            if (ship['damage'] > 0):
                labelString = "ship %s has %d damage" % (ship['name'],
                                                         ship['damage'])
                popup.add_command(label=labelString,
                          command=lambda name=ship['name']:
                          damageAllocationMenu(tkRoot, name))
            elif (ship['damage'] < 0):
                labelString = "ship %s must retreat" % (ship['name'])
                popup.add_command(label=labelString,
                          command=lambda name=ship['name']:
                          retreatMenu(tkRoot, name))

    try:
        #disable left click
        popup.post(pixel_X, pixel_Y)
    finally:
        popup.grab_set()
        pass


# PURPOSE: Delete previous and set new, phase menu
# RETURNS: none
def phaseMenu(tkRoot, gamePhase, playerPhase):
    print("Phase:", gamePhase, ", PlayerPhase:", playerPhase)
    menuBar = tkRoot.cget("menu")
    print("bar ", menuBar)
    print("")
    menuBar = tkRoot.nametowidget(menuBar)
    if (len(menuBar.children.items()) > 2):
        menuBar.delete(3)

    tkRoot.hexMap.unHiliteMap()
    tkRoot.hexMap.setRightPrivateCallBack(None, None)

    # Want to hilight who owns what on the map
    if (tkRoot.game):
        for player in tkRoot.game['playerList']:
            hiliteList = getOwnedList(tkRoot.game, player['plid'])
            for obj in hiliteList:
                tkRoot.hexMap.hiliteMap(obj['location']['x'],
                                        obj['location']['y'],
                                        player['color'], 2, None)

    phaseMenuObject = Menu(menuBar)
    player = playerTableGet(tkRoot.game, tkRoot.plid)
    if (playerPhase == 'waiting'):
        # Player is waiting on opponent. All they can do is refresh.
        phaseMenuObject.add_command(label="WAITING on opponent")
    elif (gamePhase == None):
        if (tkRoot.hCon is None):
            gamePhase = "connect"
            phaseMenuObject.add_command(label="Connect",
                                  command=lambda:connectServer(tkRoot))
        else:
            gamePhase = "start"
            phaseMenuObject.add_command(label="New",
                                  command=lambda:newGame(tkRoot))
            phaseMenuObject.add_command(label="Open",
                                  command=lambda:loadGame(tkRoot))
    elif (player is None):
        phaseMenuObject.add_command(label="Join",
                              command=lambda:playerJoinMenu(tkRoot))
    elif (gamePhase == 'creating'):
        phaseMenuObject.add_command(label="Start",
                              command=lambda:sendStartMenu(tkRoot))
        phaseMenuObject.add_command(label="ReJoin",
                              command=lambda:playerJoinMenu(tkRoot))
    elif (gamePhase == 'build'):
        assert(player)
        phaseMenuObject.add_command(label="Bases you own:")
        #Technically, its only bases that can do this
        for base in tkRoot.game['objects']['starBaseList']:
            if (base['owner'] == tkRoot.plid):
                print (base['owner'])
                labelString = "'%s'    BP left: %d" % (base['name'],
                        base['BP']['cur'])
                phaseMenuObject.add_command(label=labelString, 
                                            command=lambda baseName=base['name']:buildShip(tkRoot, baseName))
                tkRoot.hexMap.hiliteMap(base['location']['x'],
                                        base['location']['y'],
                                        player['color'], 4, None)
        phaseMenuObject.add_separator()
        for ship in tkRoot.game['objects']['shipList']:
            #if we own this star, and have a hold, we should be able to load/unload goods.
            star = findObjectsInListAtLoc(tkRoot.game['objects']['starList'],
                                          ship['location']['x'],
                                          ship['location']['y'])
            if (star and star['owner'] == tkRoot.plid and ship['H']['cur'] > 0):
                labelString = "'%s'    Hauling: %d/%d" % (ship['name'],
                        ship['Hauled'], ship['H']['cur'] * 10)
                phaseMenuObject.add_command(label=labelString,
                        command=lambda thisShip=ship, thisStar=star:loadCargo(tkRoot,thisStar,thisShip))
                tkRoot.hexMap.hiliteMap(ship['location']['x'],
                                        ship['location']['y'],
                                        player['color'], 2, None)

        phaseMenuObject.add_separator()
        phaseMenuObject.add_command(label="Ready",
                              command=lambda:sendReadyMenu(tkRoot))
        tkRoot.hexMap.setRightPrivateCallBack(buildPopUp, tkRoot)

    elif (gamePhase == 'move'):
        # is it our turn to move?
        assert(player)
        if player['phase'] == "move":
            phaseMenuObject.add_command(label="Ships you own:")
            for ship in tkRoot.game['objects']['shipList']:
                if (ship['owner'] == tkRoot.plid):
                    if (ship['WG']['cur'] == True):
                        labelString = "'%s'    Moves left: %d/%d" % (ship['name'],
                                                                     ship['moves']['cur'],
                                                                     math.ceil(ship['PD']['cur']/2))
                        phaseMenuObject.add_command(label=labelString, command=lambda shipName=ship['name']: moveMenu(tkRoot, shipName))
                    else:
                        #find a way to get system ships on to warp ships
                        labelString = "System Ship:'%s'    Moves left: N/A" % (ship['name'])
                        #TODO: make hCon more secure
                        phaseMenuObject.add_command(label=labelString,
                                command=lambda name=ship['name']: loadShip(tkRoot, ship, tkRoot.game['objects']['shipList']))


            phaseMenuObject.add_command(label="Ready",
                                  command=lambda:sendReadyMenu(tkRoot))
            #enable the move right click stuff.
            tkRoot.hexMap.setRightPrivateCallBack(movePopUp, tkRoot)

    elif (gamePhase == 'combat'):

        assert(player)
        # They make their choices and submit orders.
        # The user will still need to select all the other locations and
        # give orders. Then they will have to wait for results. (That
        # requires a response from the other user)
        #
        # Should they make commands for each location and submit all
        # at once or can they do them piecemeal? All at once makes
        # the code easier. So instead of a "ready" menu command there should
        # be a "submitOrders" command? We'll then need to store up all their
        # orders from each battle screen? Combine them for sending and
        # prevent them from submitting multiple orders for the same ship
        # ... I guess for initial implementation if they have multiple orders
        # for the same ship we assert (or just use the first one? Or just
        # let them?)
        #

        # Find all locations with "combat". That is all locations that
        # have ships (or bases, or stars or things) that are owned by
        # multiple players (unowned could be considered another player?)
        # Now that we have a list of all locations for combat ....
        # We need a list of each thing involved in combat at each location
        # (So an array of locations each with a list of "things" involved)
        conflictList = getConflictList(tkRoot.game['objects'])
        print("conflicts:", conflictList)

        # If the conflict list is *empty* then there is no point in a combat
        # phase. Automatically move on.
        if (not conflictList):
            print("conflicts are empty. send the ready command and redo menus")
            tkRoot.event_generate("<<sendReady>>", when='tail')
            print("conflicts are empty. post send event")

        # I want to display each battle location in the phase menu and
        # highlight the location in red. Like red outline the hex
        # The user can select any location and that will take them to
        # a battle screen. We should set the left (or right) click
        # on the location so it brings up the battle screen.
        phaseMenuObject.add_command(label="Conflicts:")
        for conflict in conflictList:
            conflictDict, nonShipList = organizeConflict(conflict)
            print(dataModel.playerNameGet(tkRoot.game, tkRoot.plid))
            print(conflictDict)
            print("NONSHIP")
            print(nonShipList)
            #who am I,and who is my enemy?
            friendlyShips = []
            if (tkRoot.plid in conflictDict):
                friendlyShips = conflictDict[tkRoot.plid]
            enemyShips = []
            for key in conflictDict:
                if key != tkRoot.plid:
                    for ship in conflictDict[key]:
                        enemyShips.append(ship)

            #make sure that the colors align with the players in the conflict dict
            i = 0
            colors = [""]*6
            belligerentIDs = list(conflictDict.keys())
            belligerents = [playerTableGet(tkRoot.game, ID) for ID in belligerentIDs]
            while (i < 6):
                if len(belligerents) > 1:
                    colors[i] = belligerents[i % len(belligerents)]['color']
                else:
                    colors[i] = belligerents[0]['color']
                i += 1

            tkRoot.hexMap.specialHiliteMap(int(conflict[0]['location']['x']),
                                    int(conflict[0]['location']['y']),
                                    colors[0],
                                    colors[1],
                                    colors[2],
                                    colors[3],
                                    colors[4],
                                    colors[5],
                                    4, None)

            if enemyShips:
                labelString = "%d Friendlies vs %d Enemies" % (len(friendlyShips), len(enemyShips))
                phaseMenuObject.add_command(label=labelString,
                                command=lambda friendlyShips=friendlyShips,
                                enemyShips=enemyShips:
                                combatAtLocation(tkRoot,
                                                 friendlyShips,
                                                 enemyShips))
            elif nonShipList:
                labelString = "%d Friendlies can conquer this sector" % (len(friendlyShips))
                bases = []
                for base in nonShipList:
                    bases.append(base['name'])
                phaseMenuObject.add_command(label=labelString,
                                command=lambda friendlyShips=friendlyShips,
                                bases=bases:
                                conquestAtLocation(tkRoot,
                                                   friendlyShips,
                                                   bases))
            else:
                assert(0)

        phaseMenuObject.add_command(label="Ready",
                              command=lambda:sendCombatReady(tkRoot))

        tkRoot.hexMap.setRightPrivateCallBack(combatPopUp, tkRoot)

    elif (gamePhase == 'damageselection'):
        # Find all of *my* ships that are damaged
        # Pop up a menu with each damaged ship? (Each location with
        # damage? At some point that is probably better. You kind of want
        # to see combat results. What tactic did I hit/miss with? What
        # tactic did my opponent hit/miss with)
        # So you have a list of myships/yourships, each ships orders.
        # each attacks results. Then you select your own ship and
        # get a dialog to allocate the damage results.
        allShipsSafe = True
        for ship in tkRoot.game['objects']['shipList']:
            if (ship['owner'] == tkRoot.plid):
                if (ship['damage'] > 0):
                    allShipsSafe = False
                    labelString = "ship %s has %d damage" % (ship['name'],
                                                         ship['damage'])
                    phaseMenuObject.add_command(label=labelString,
                                        command=lambda name=ship['name']:
                                        damageAllocationMenu(tkRoot, name))
                elif (ship['damage'] < 0):
                    allShipsSafe = False
                    labelString = "ship %s must retreat" % (ship['name'])
                    phaseMenuObject.add_command(label=labelString,
                                        command=lambda name=ship['name']:
                                        retreatMenu(tkRoot, name))
                else:
                    pass

        # don't let the user progress if there is unallocated damage
        if (allShipsSafe):
            phaseMenuObject.add_command(label="Ready",
                                        command=lambda:sendReadyMenu(tkRoot))

        tkRoot.hexMap.setRightPrivateCallBack(damageSelectionPopUp, tkRoot)

    elif (gamePhase == 'victory'):
        gamePhase = "Game Over. You are a " + playerPhase
    else:
        print("BAD PHASE", gamePhase)
        gamePhase = ""

    phaseMenuObject.add_command(label="Refresh", command=lambda:refresh(tkRoot))

    menuBar.add_cascade(label="Phase " + gamePhase, menu=phaseMenuObject)

# PURPOSE: Create menu GUI elements
# RETURNS: none
def addMenus(tkRoot):
    menuBar = Menu(tkRoot)
    print("winfo", menuBar.winfo_id())

    fileMenu = Menu(menuBar)
    print("filemenu", fileMenu)

    fileMenu.add_command(label="Connect", command=lambda:connectServer(tkRoot))
    fileMenu.add_command(label="New", command=lambda:newGame(tkRoot))
    fileMenu.add_command(label="Open", command=lambda:loadGame(tkRoot))
    fileMenu.add_command(label="Save", command=lambda:saveGame(tkRoot.game))
    fileMenu.add_separator()
    fileMenu.add_command(label="Refresh", command=lambda:refresh(tkRoot))
    fileMenu.add_separator()
    fileMenu.add_command(label="Exit", command=lambda:exitProgram(tkRoot))

    menuBar.add_cascade(label="File", menu=fileMenu)

    helpMenu = Menu(menuBar)
    helpMenu.add_command(label="About", command=aboutHelp)
    helpMenu.add_command(label="Help", command=helpHelp)
    print("helpMenu", helpMenu)

    menuBar.add_cascade(label="Help", menu=helpMenu)

    tkRoot.config(menu=menuBar)
    tkRoot.event_generate("<<updateWWMenu>>", when='tail')

# handle <Configure> event
# Redraw the map after a window resize
def Configure(event, tkRoot):
    if (tkRoot.configureDelay):
        tkRoot.after_cancel(tkRoot.configureDelay)
    tkRoot.hexMap.handleResizeEvent(event)
    tkRoot.configureDelay = tkRoot.after(500, lambda : tkRoot.event_generate("<<updateWWMenu>>", when='tail'))

# PURPOSE: Just make a function out of the main code. It doesn't
#          seem right without that.
# RETURNS: ?? hmmm
def main():

    # Instance of tkinter to do GUI stuff
    tkRoot = Tk()
    tkRoot.title("WarpWar")
    tkRoot.hCon = None
    tkRoot.plid = None
    tkRoot.hPlayerAi = None
    tkRoot.hexMap = None
    tkRoot.game = None
    tkRoot.configureDelay = None

    #get the user's profile.
    tkRoot.cfg = ConfigHandler("warpwar.ini")

    tkRoot.battleOrders = {}
    tkRoot.bind("<<updateWWMenu>>", lambda event :updateWWMenu(event, tkRoot))
    tkRoot.bind("<<sendReady>>", lambda event :sendReady(event, tkRoot))
    tkRoot.bind("<<sendStart>>", lambda event :sendStart(event, tkRoot))


    # menu bar
    addMenus(tkRoot)

    # Create A "PanedWindow" on top of a frame to fit everything into
    #
    # +------------------------------------+
    # |    PANED WINDOW                    |
    # |                                    |
    # |                                    |
    # +------------------------------------+
    # |       button frame                 |
    # +------------------------------------+
    tkRoot.topPane = PanedWindow(tkRoot, orient='horizontal', bg='blue')
    tkRoot.buttonFrame = Frame(tkRoot)
    tkRoot.buttonFrame.pack(side="bottom")

    # It is important to pack the topPane LAST (but at the top) so that
    # the buttons don't disappear when shrinking the whole window
    tkRoot.topPane.pack(side="top", expand=YES, fill=BOTH)

    # Create add a map to the top paned window on the left
    # and add another paned window on the right
    # +------------------------------------+
    # |                     |              |
    # |   map window        |  info pane   |
    # |                     |              |
    # +------------------------------------+
    tkRoot.hexMap = hexMap(tkRoot.topPane, tkRoot, 10, 10)
    tkRoot.infoPane = PanedWindow(tkRoot, orient='vertical')
    tkRoot.topPane.add(tkRoot.hexMap, stretch='always')
    tkRoot.topPane.add(tkRoot.infoPane, stretch='always')

    # Call back for when the map grows/shrinks
    tkRoot.hexMap.bind("<Configure>", lambda event, tkRoot=tkRoot :Configure(event, tkRoot))


    # Create another Pane in the right PanedWindow(infoPane)
    # for displaying history. There is, history, info and server,
    # and playerai ...  we can add others
    # +--------------------+
    # |                    |
    # |   Future pane1     |
    # +------------------- +
    # |   Future pane2     |
    # +------------------- +
    # |                    |
    # |   history pane     |
    # +--------------------+
    tkRoot.hexInfoFrame = hexpane.hexpane(tkRoot.infoPane, borderwidth=1, relief="sunken")
    tkRoot.infoPane.add(tkRoot.hexInfoFrame, stretch='always')
    tkRoot.histFrame = histpane.history(tkRoot.infoPane, borderwidth=1, relief="sunken")
    tkRoot.infoPane.add(tkRoot.histFrame, stretch='always')

    # Put buttons into the button frame
    tkRoot.quitButton = Button(tkRoot.buttonFrame, text = "Quit",
                  command = lambda :exitProgram(tkRoot))
    tkRoot.quitButton.grid(row=0, column=0, padx=15)

    tkRoot.playersButton = Button(tkRoot.buttonFrame, text = "Players",
                                  command = lambda :popupPlayers(tkRoot))
    tkRoot.playersButton.grid(row=0, column=1, padx=15)

    # Display default game info on the map
    tkRoot.hexMap.updateMap(tkRoot.game)

    tkRoot.tooltipX = 0
    tkRoot.tooltipY = 0
    tkRoot.tooltipCount = 0
    tkRoot.tooltip = None
    tkRoot.after(1000, lambda :tooltip(tkRoot))


    # at the moment this does nothing valuable
    #foo = GameInfo(tkRoot.hexMap.grid_width,
                   #tkRoot.hexMap.grid_height,
                   #tkRoot.game['playerList'])

    # Let tkinter main loop run forever and handle input events
    tkRoot.mainloop()

    # it is better to wait for child threads here (after GUI ends)
    # rather than in the GUI code. That created deadlocks.
    if (tkRoot.hCon):
        tkRoot.hCon.join()
        tkRoot.hCon = None
    if (tkRoot.hPlayerAi):
        tkRoot.hPlayerAi.join()
        tkRoot.hPlayerAi = None


# Start the main function
if __name__ == "__main__":
   main()
