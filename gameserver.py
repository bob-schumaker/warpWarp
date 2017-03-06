# class to handle game commands
# Game state goes from:
# Nil
# Game created and ready for players
# Players join? Select starting locations?
# Building phase,
# Check finished building, Waiting for other players to finish building
# Movement phase,
# Check finished movement, wait for other players to finish moving
# Combat phase
#   Choose battles? Battles chosen
#   Make combat plans,
#   submit combat plans, wait for oppoent to finish combat plans
#   Results of battle reported
#   Select damage,
#   submit damage selection, wait for opponent to finish damage selections
#   All battles finished? On to next battle.
#
# Done? Back to Build phase
#
#
# PHASE:
# nil
# creating
# build
# move
# combat
# battle
# damageselection


import sys
sys.path.append("/home/ahw/views/warpWar/test")

import json
import samplegame
import ijk

# PURPOSE: look up ship name in game ship list
# RETURNS: entry of ship
def findShip(game, shipName):
   for ship in game['objects']['shipList']:
        if ship['name'] == shipName:
            return ship
   return None

# class to handle game commands
class gameserver:

    # PURPOSE: Called for class construction
    # RETURNS: none
    def __init__(self):
        self.gameContinues = True
        self.game = samplegame.sampleGame

    # PURPOSE: Have we received the quit command
    # RETURNS: true if no quit command yet
    def gameOn(self):
        return self.gameContinues

    # PURPOSE: Return the JSON representing the entire game
    # RETURNS: game state as a JSON string
    def gameJson(self):
        return json.dumps(self.game, ensure_ascii=False)

    # PURPOSE: Interpret JSON command and do something
    # RETURNS: true for properly parsed command
    def parseCmd(self, jsonStr):
        try:
            root = json.loads(jsonStr)
        except Exception as error:
            print("JSON parse error for ", jsonStr, "\n")
            return False

        cmd = root['cmd']
        cmdStr = cmd['cmd']
        print("CMD:", cmdStr, "PHASE:", self.game['state']['phase'])

        if cmdStr == 'quit':
            print("quitCommandRecieved")

            # This cmd doesn't save anything. Call save if you want to save
            self.game['state']['phase'] = "nil"
            self.gameContinues = False

        elif cmdStr == 'ping':
            # simple test to see if server responds. So print and respond
            print("ping")

        elif cmdStr == 'newplayer':
            # New player requests to join.
            # I guess we would look at the game state? Hmmm
            # What about a player joining a previously saved game?
            # Input? Player name and potentially player specific options
            # What player specific options? IP:port?
            assert( (self.game['state']['phase'] == "nil") or
                    (self.game['state']['phase'] == "creating")
                  )
            newPlayer = cmd['name']
            print("newPlayer", newPlayer)
            playerFound = False
            for player in self.game['playerList'] :
                if (player['name'] == newPlayer):
                    playerFound = True
                    print("player already exists!", player)
                    break

            if playerFound:
                assert(player['phase'] == "nil")
                player['phase'] = "creating"
            else:
                self.game['playerList'].append({'name':  newPlayer,
                                                'phase': "creating"})

        elif cmdStr == 'newgame':
            # What to do? Offer to save current game? NO! this is the server,
            # do as commanded
            # erase current game/dictionary
            # Start empty
            # Input? Would be list of options for game
            # Should we prevent this? Perhaps block it? Only permit it
            # if there is only one connected player?
            #
            # Need to be given the name of the game?
            # Warn/Error if current game hasn't been saved (is dirty)
            gameName = cmd['name']
            assert(self.game['state']['phase'] == "nil")
            self.game['state']['phase'] = "creating"
            # TODO probably need things like game options???
            # TODO lots of options, right?

        elif cmdStr == 'start':
            # Basically just change state so players can begin building
            # and playing
            assert(self.game['state']['phase'] == "creating")
            self.game['state']['phase'] = "build"

        elif cmdStr == 'buildship':
            # Now we get to fun stuff
            # Check for proper state to see if player permitted to build.
            # Validate a legal build. Does player have the money?
            # Input? ... this is a lot... The entire ship? We would have
            # to calculate the cost based on the options and validate it.
            # We would have to deduct the cost from the players total.
            # Of course need to see if it is a valid ship to begin with
            # TODO lots of parameters!
            assert(self.game['state']['phase'] == "build")

        elif cmdStr == 'ready':
            # A generic cmd used to end several phases
            playerName = cmd['name']
            print("player", playerName, "done with phase", self.game['state']['phase'])

            # Based on current phase what do we do?
            if (self.game['state']['phase'] == "creating"):
                # Record ready for given player
                print("Player creating. What phase is next?")
                for player in self.game['playerList'] :
                    if (player['name'] == playerName):
                        assert(player['phase'] == "creating")
                        player['phase'] = "build"

                # If all players are in build then the game phase is build
                playerFound = False
                for player in self.game['playerList'] :
                    if (player['phase'] != "build") and (player['phase'] != "nil"):
                        playerFound = True
                        break;

                if not playerFound:
                    self.game['state']['phase'] = "build"

            elif (self.game['state']['phase'] == "build"):
                # Given player can no longer build and must wait
                # When all players ready AUTO move to move phase
                self.game['state']['phase'] = "move"
            elif (self.game['state']['phase'] == "move"):
                # Given player can no longer move and must wait
                # When all players ready AUTO move to combat phase
                self.game['state']['phase'] = "combat"
            elif (self.game['state']['phase'] == "combat"):
                # Given player must wait for other players to be ready?
                # When all players ready AUTO move to battle phase
                self.game['state']['phase'] = "battle"
                # What if there is no combat? Probably go on to build
                self.game['state']['phase'] = "build"
            elif (self.game['state']['phase'] == "battle"):
                # Given player can no longer give orders and must wait
                # When all players ready AUTO move to damageSelection phase
                # or resolve combat phase? Is there such a phase?
                self.game['state']['phase'] = "damageselection"
            else:
                print("Invalid phase for 'ready'")
                assert(False)

        elif cmdStr == 'moveship':
            # Input? ShipID, new location of ship? Movement vector?
            # Is it legal to move? (Proper turn sequence. Valid location on
            # map? Currently in combat? Does move cause combat? (meaning ship
            # halts immediately))
            # Deduct movement from ship
            name = cmd['name']
            x = cmd['x']
            y = cmd['y']

            assert(self.game['state']['phase'] == "move")

            ship = findShip(self.game, name)
            if (ship is None):
                print("error: Ship not found", name)
                return False

            si,sj,sk = ijk.XYtoIJK(x, y)
            fi,fj,fk = ijk.XYtoIJK(ship['location']['x'], ship['location']['y'])
            delta = int((abs(si-fi) + abs(sj-fj) + abs(sk-fk)) / 2)

            print(" delta", delta, ship['location']['x'], ship['location']['y'],
                                   x, y)
            ship['location']['x'] = x
            ship['location']['y'] = y
            ship['moves']['cur'] = ship['moves']['cur'] -delta 

        elif cmdStr == 'combatorders': # Per ship? All ships?
            # A combat instruction
            # Check for proper state. Are there existing orders?
            # Have all ships in combat been given orders?
            # Have all opponents ships in *this* combat been given orders?
            # Input? ShipID, combat command (fire, move, shields ...)
            # TODO many more parameters
            assert(self.game['state']['phase'] == "battle")

            # When all damage has been selected ... by all players ...
            # move to battle .... or retreat ... or combat over ... or next
            # battle?

        elif cmdStr == 'acceptdamage':
            # Deduct combat damage
            # Input? ShipID, damage deducted from each component
            # Did they deduct enough damage?
            # Do they have more ships with damage to deduct?
            # TODO many more parameters
            assert(self.game['state']['phase'] == "damageselection")

        elif cmdStr == 'savegame':
            # Write file ... who is responsible for game save?
            # I Don't want to load/restore game that is stored on the server
            # ... well, I would like to but that API would be a pain.
            # I'd have to do all the directory I/O work. Remember the game
            # server has no UI. So I would read files and directories
            # off of the server and then let the client navigate, select and
            # choose save/load
            #
            # Given a file name write that file to some save location
            # Mark the game as saved (not dirty)
            # It is possible that the name of the game (name of the file)
            # is already part of the game so you wouldn't need to provide
            # the name.
            #
            # Server does nothing with saveGame. The client must save the game
            print("saveGame")
        elif cmdStr == 'restoregame':
            # Because games are saved/restored on client ...
            # This would do nothing. Just like saveGame
            #
            # Given the name of a file/game.
            # restore that game overwriting the current game
            # Warn/Error if current game hasn't been saved (is dirty)
            print("restoreGame")
        elif cmdStr == 'listgames':
            # Because games are saved/restored on client ...
            # This would do nothing. Just like saveGame
            #
            # List all of the saved games
            print("listGames")
        elif cmdStr == 'loadgame':
            # Offer to save current game?
            # Bring up selection dialog
            # load game overwriting existing game
            #
            # Like, newGame check for permission.
            # Input? Would be an entire JSON game
            # We should probably do some kind of validation but
            # this would just be pulling in the JSON and
            # translating it to the dict.
            #
            # Warn/Error if current game hasn't been saved (is dirty)
            print("loadGame")
        elif cmdStr == 'playerleave':
            # Player is quiting
            # We could check for permission but I don't think so.
            # This is informational
            # Input? Player name? Some unique player key code for security?
            print("playerLeaving")

        else:
            print("Not a legal command '", cmdStr, "'")
            return False

        return True
