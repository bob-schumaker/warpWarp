from connect import *
from cmds import warpWarCmds
import tkinter as tk
from tkinter.simpledialog import *

class loadShipMenu(Dialog):

    # PURPOSE:
    # RETURNS:
    def __init__(self, master, ship, shipList):
        self.ship = ship
        self.shipList = shipList
        #TODO: what if hCon is null?
        self.location = [self.ship['location']['x'], self.ship['location']['y']]
        Dialog.__init__(self, master)

    def body(self, master):
        #just a drop down list with ship names
        self.motherVar = StringVar(master)
        #but not any ships! only the ones in this hex
        motherList = [ship for ship in self.shipList if ship['location']['x'] == self.location[0] and ship['location']['y'] == self.location[1]]
        mother = OptionMenu(master, self.motherVar, 
                *[ship['name'] for ship in motherList if ship['SR']['cur'] >= 1])
        mother.grid()
