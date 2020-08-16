#!/usr/bin/env python
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class Gameserver(DatagramProtocol):
    addresslist = []
    def removeclient(self, client, data):
        if data == "BYE":
            self.addresslist.remove(client)
            self.transport.write("OK", client)
            print "Client (IP: %s, Port: %s) Removed." % (client[0],client[1])
            
            return 1
        else:
            return 0
            
    def addclient(self, client):
        # Add the client to database
        if self.addresslist.count(client) == 0:
            self.addresslist.append(client)
            print "Client (IP: %s, Port: %s) Added." % (client[0],client[1])
            return 1
        else:
            return 0
            
    def sendtoall(self, client, data):
        # Send package to all clients.
        for listclient in self.addresslist:
            if listclient != client:
                self.transport.write(data, listclient)
            
    def datagramReceived(self, data, (host, port)):
        client = (host, port)
        self.addclient(client)
        self.removeclient(client, data)
        self.sendtoall(client, data)
        
reactor.listenUDP(9999, Gameserver())
reactor.run()
