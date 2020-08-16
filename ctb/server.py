#!/usr/bin/python
import netgamelib
import time
print "NetGameLib Verson", netgamelib.version
class test:
    testvar = "lol"
class CTBserver(netgamelib.Server):
    def gameloop(self):
        t = test()
        self.sendtoall([t], excludeself=False)
    def DataRecieved(self, data, rawdata, client):
        print "Recieved", data
        if data == "list":
            self.sendtoone(self.listclients(), client)
            return
        if data == "disconnect":
            result = self.removeclient(client)
            self.sendtoone(result, client)
            return
        self.sendtoall(data, client, excludeself=False)
GS = CTBserver()
GS.listen(9999)
