# Server for WarpWar game
#
# Gui Test driver for Server thread
#

# Imports
# server thread for sending data to and fro
from server import srvrThrd
from playerAi import playerAiThrd
import socket
import tkinter as tk
import threading
import queue as Q
import ConfigHandler

# GUI thread for management
class ServerApp(threading.Thread):
    
    # PURPOSE: Called for class construction
    # RETURNS: none
    def __init__(self, tkRoot):
        self.root = tk.Toplevel()
        self.Q = Q.Queue()
        self.hNET = None
        self.hPlayerAi = None
        self.cfg = ConfigHandler.ConfigHandler('warpwar.ini')
        print(self.cfg.Server.serverIP)
        print(self.cfg.Server.serverPort)
        print(self.cfg.PlayerAI.name)

        #threading.Thread.__init__(self, name="ServerMyTkApp")
        #self.start()
        
    # PURPOSE: Button handler. The Quit button
    #          call this when "Quit" button clicked
    # RETURNS: I don't know.
    def quitCB(self):
        print("STest: quiting?")
        if (self.hNET is not None) :
            self.hNET.quit()
        if (self.root is not None) :
            self.root.quit()
        if (self.hPlayerAi is not None) :
            self.hPlayerAi.quit()
        print("STest: Server Gui exit")

    # PURPOSE: Start the network server thread
    # RETURNS: nothing
    def startServer(self):
        print("STest: start server")
        self.cfg.Server.serverIP = self.host.get()
        self.cfg.Server.serverPort = self.port.get()
        self.cfg.PlayerAI.name = self.player2Name.get()
        self.cfg.saveConfig()
        self.hNET = srvrThrd(self.cfg.Server.serverIP, int(self.cfg.Server.serverPort), self)

    # PURPOSE: Start the AI Player
    # RETURNS: nothing
    def startAI(self):
        print("STest: start AI")
        self.hPlayerAi = playerAiThrd(self.player2Name.get(),
                                      self.host.get(),
                                      int(self.port.get()))

    # PURPOSE: Construct all the GUI junk
    # RETURNS: nothing
    def initGui(self):
        self.root.title("Server IP:port")
        self.root.protocol("WM_DELETE_WINDOW", 
                              lambda :self.quitCB())

        tmp = tk.Label(self.root, text="Server: ")
        tmp.grid(row=1, column=0)
        print("init gui!")
        print(self.cfg.Server.serverIP)
        print(self.cfg.Server.serverPort)
        print(self.cfg.PlayerAI.name)

        self.host = tk.StringVar()
        self.host.set(self.cfg.Server.serverIP)
        self.serverEntry = tk.Entry(self.root, textvariable=self.host)
        self.serverEntry.grid(row=1, column=1)
        print(self.host.get())

        self.port = tk.StringVar()
        self.port.set(self.cfg.Server.serverPort)
        self.portEntry = tk.Entry(self.root, textvariable=self.port)
        self.portEntry.grid(row=1, column=2)

        # for starting the AI player
        tmp = tk.Label(self.root, text="AI Name: ")
        tmp.grid(row=2, column=0)
        self.player2Name = tk.StringVar()
        self.player2Name.set(self.cfg.PlayerAI.name)
        self.player2Entry = tk.Entry(self.root, textvariable=self.player2Name)
        self.player2Entry.grid(row=2, column=1)
        # Create a Start button
        self.startAIBtn = tk.Button(self.root, text = "StartAI",
                                 command = lambda :self.startAI())
        self.startAIBtn.grid(row=2, column=2)

        tmp = tk.Label(self.root, text="Send Msg: ")
        tmp.grid(row=3, column=0)
        
        self.sendMsg = tk.StringVar()
        self.sendMsg.set("")
        self.sendMsgEntry = tk.Entry(self.root, textvariable=self.sendMsg)
        self.sendMsgEntry.grid(row=3, column=1)
        
        tmp = tk.Label(self.root, text="Received From: ")
        tmp.grid(row=5, column=0)
        
        self.recvFrom = tk.StringVar()
        self.recvFrom.set("")
        self.recvFromEntry = tk.Entry(self.root, textvariable=self.recvFrom)
        self.recvFromEntry.grid(row=5, column=1)

        tmp = tk.Label(self.root, text="Received Msg: ")
        tmp.grid(row=6, column=0)
        
        self.recvMsg = tk.StringVar()
        self.recvMsg.set("")
        self.recvMsgEntry = tk.Entry(self.root, textvariable=self.recvMsg)
        self.recvMsgEntry.grid(row=6, column=1)

        # Create a Start button
        self.start = tk.Button(self.root, text = "Start",
                              command = lambda :self.startServer())
        self.start.grid(row=7, column=1)

        # Create a quit button (obviously to exit the program)
        self.quit = tk.Button(self.root, text = "Quit",
                              command = lambda :self.quitCB())
        self.quit.grid(row=7, column=2)

    # PURPOSE: for external parties to send a message to the GUI thread
    #          The socket server uses this
    # RETURNS: none
    def displayAddr(self, msg):
        self.Q.put("addr")
        self.Q.put(msg)
        
    # PURPOSE: for external parties to send a message to the GUI thread
    #          The socket server uses this
    # RETURNS: none
    def displayMsg(self, msg):
        self.Q.put("msg")
        self.Q.put(msg)        

    # PURPOSE: Display data from my GUI Q in box
    # RETURNS: none
    def handleDisplayAddr(self):
        addr = self.Q.get()
        self.recvFrom.set(addr)
        
    # PURPOSE: Display data from my GUI Q in box
    # RETURNS: none
    def handleDisplayMsg(self):
        msg = self.Q.get()
        self.recvMsg.set(msg)
        
    # PURPOSE: drain the Q
    #    While this returns. It also starts a timer
    #    that will call this function again
    # RETURNS: none
    def poll(self):

        while not self.Q.empty():
            cmd = self.Q.get()
            if (cmd == "addr"):
                self.handleDisplayAddr()
            elif (cmd == "msg"):
                self.handleDisplayMsg()

        self.root.after(2000, self.poll)
    
    # PURPOSE: automatically called by base thread class, right?
    #     create the GUI, wait for msgs on a timer, run the tkinter
    #     thing so the GUI responds to the user
    # RETURNS: none
    def run(self):
        self.initGui()
        self.poll()
        print("STest: POLL is done?")


# PURPOSE: start up stuff...
# RETURNS: none?
def main():
    root = tk.Tk()
    root.withdraw()
    hGui = ServerApp(root)
    hGui.initGui()
    hGui.poll()
    root.mainloop()
    print("STest: Main program exiting")

# Start the main function
if __name__ == "__main__":
   main()
