
import tkinter as tk
from tkinter.simpledialog import *

class build(Dialog):

    # PURPOSE:
    # RETURNS:
    def __init__(self, master, base):
        self.base = base
        self.remaining = self.base['stockpile']
        Dialog.__init__(self, master)

    # PURPOSE:
    # RETURNS:
    def makeHeader(self, headerFrame):
        headerFrame.grid(columnspan=2)
        totalFrame = Frame(headerFrame, relief=RIDGE, bd=10)
        TotalW = Label(totalFrame, text="Total BP:%d" % self.base['stockpile'])
        TotalW.grid()
        totalFrame.grid(row=0,column=1)

        spentFrame = Frame(headerFrame, relief=RIDGE, bd=10)
        self.spentW = Label(spentFrame, text="Used BP:%d" % 0)
        self.spentW.grid()
        spentFrame.grid(row=0,column=2)

        remainingFrame = Frame(headerFrame, relief=RIDGE, bd=10)
        self.remainingW = Label(remainingFrame, text="Remaining BP:%d" % self.base['stockpile'])
        self.remainingW.grid()
        remainingFrame.grid(row=0,column=3)

    # PURPOSE:
    # RETURNS:
    def makeSpinners(self, spinFrame):
        self.spinList = []

        tmpLbl = Label(spinFrame, text="SHIP NAME")
        tmpLbl.grid(row=1, column=0)
        self.shipNameEntry = Entry(spinFrame)
        self.shipNameEntry.grid(row=1, column=1)

        tmpLbl = Label(spinFrame, text="POWER DRIVE")
        tmpLbl.grid(row=2, column=0)
        self.pwrSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.spinList.append(self.pwrSpn)
        self.pwrSpn.grid(row=2, column=1)

        tmpLbl = Label(spinFrame, text="BEAMS")
        tmpLbl.grid(row=3, column=0)
        self.beamSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.beamSpn.grid(row=3, column=1)
        self.spinList.append(self.beamSpn)

        tmpLbl = Label(spinFrame, text="SCREENS")
        tmpLbl.grid(row=4, column=0)
        self.screenSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.screenSpn.grid(row=4, column=1)
        self.spinList.append(self.screenSpn)

        tmpLbl = Label(spinFrame, text="ELECTRONIC COUNTERMEASURES")
        tmpLbl.grid(row=5, column=0)
        self.ecmSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.ecmSpn.grid(row=5, column=1)
        self.spinList.append(self.ecmSpn)

        tmpLbl = Label(spinFrame, text="TUBES")
        tmpLbl.grid(row=6, column=0)
        self.tubeSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.tubeSpn.grid(row=6, column=1)
        self.spinList.append(self.tubeSpn)

        tmpLbl = Label(spinFrame, text="MISSLES (x3)")
        tmpLbl.grid(row=7, column=0)
        self.mslSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.mslSpn.grid(row=7, column=1)
        self.spinList.append(self.mslSpn)

        tmpLbl = Label(spinFrame, text="ARMOR (x2)")
        tmpLbl.grid(row=8, column=0)
        self.armorSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.armorSpn.grid(row=8, column=1)
        self.spinList.append(self.armorSpn)

        tmpLbl = Label(spinFrame, text="CANNONS")
        tmpLbl.grid(row=9, column=0)
        self.cannonSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.cannonSpn.grid(row=9, column=1)
        self.spinList.append(self.cannonSpn)

        tmpLbl = Label(spinFrame, text="SHELLS (x6)")
        tmpLbl.grid(row=10, column=0)
        self.shellSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.shellSpn.grid(row=10, column=1)
        self.spinList.append(self.shellSpn)

        tmpLbl = Label(spinFrame, text="SYSTEMSHIP RACKS")
        tmpLbl.grid(row=11, column=0)
        self.srSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.srSpn.grid(row=11, column=1)
        self.spinList.append(self.srSpn)

        tmpLbl = Label(spinFrame, text="HOLDS")
        tmpLbl.grid(row=12, column=0)
        self.holdSpn = Spinbox(spinFrame, from_=0, to=self.remaining, state="readonly", command=self.updateSpinners)
        self.holdSpn.grid(row=12, column=1)
        self.spinList.append(self.holdSpn)

        tmpLbl = Label(spinFrame, text="REPAIR BAYS (1/5 BP)")
        tmpLbl.grid(row=13, column=0)
        self.rpSpn = Spinbox(spinFrame, from_=0, to=int(self.remaining / 5), state="readonly", command=self.updateSpinners)
        self.rpSpn.grid(row=13, column=1)
        #self.spinList.append(self.rpSpn) we treat this one special

        spinFrame.grid()

    # PURPOSE:
    # RETURNS:
    def updateSpinners(self):
        used = 0
        for spinner in self.spinList:
            used = used + int(spinner.get())

        used = used + 5 * int(self.rpSpn.get())

        for spinner in self.spinList:
            spinner.config(to=self.base['stockpile'] - used + int(spinner.get()))

        self.rpSpn.config(to=int((self.base['stockpile'] - used)/5) + int(self.rpSpn.get()))

        self.spentW.config(text="Used BP:%d" % used)
        self.remainingW.config(text="Remaining BP:%d" % (self.base['stockpile'] - used))

    # PURPOSE:
    # RETURNS:
    def body(self, master):
        #have a bunch of spinboxes and checkboxes
        statusFrame = Frame(master)
        self.makeHeader(statusFrame)
        spinFrame = Frame(master)
        self.makeSpinners(spinFrame)

    # PURPOSE:
    # RETURNS:
    def validate(self):
        print("validate build")
        return True

    # PURPOSE:
    # RETURNS:
    def apply(self):
        print("apply build")
        self.ship =  {
             'name': self.shipNameEntry.get(),
             'type': "ship",
             'location': {'x':self.base['location']['x'], 'y':self.base['location']['y']},
             'image':"warpship.png",
             'owner': self.base['owner'],
             'techLevel': 1,
             'moves': {'max': int(self.pwrSpn.get()), 'cur': int(self.pwrSpn.get())},   # relates to PowerDrive
             'PD':{'max':5, 'cur':5},       # PowerDrive
             'WG':{'max':True, 'cur':True}, # Warp Generator
             'B': {'max':3, 'cur':3},       # Beams
             'S': {'max':2, 'cur':2},       # Screens (Shields)
             'E': {'max':2, 'cur':2},       # Electronic Counter Measures (New)
             'T': {'max':3, 'cur':3},       # Tubes
             'M': {'max':7, 'cur':7},       # Missiles
             'A': {'max':2, 'cur':2},       # Armor (New)
             'C': {'max':1, 'cur':1},       # Cannons (New)
             'SH':{'max':2, 'cur':2},       # Shells (New)
             'SR':{'max':3, 'cur':3},       # System Ship Racks
             'H': {'max':1, 'cur':1},       # Holds (New)
             'R': {'max':1, 'cur':1},       # Repair Bays (New)
             'visibility':[ {'player':"ahw",  'percent':100},
                            {'player':"bearda", 'percent':30},
                          ],
            }
        print (self.ship)

class menuBuilder:
    def __init__(self, tkRoot, base):

        self.base = base
        self.tkRoot = tkRoot

    def __call__(self):
        build(self.tkRoot, self.base)

