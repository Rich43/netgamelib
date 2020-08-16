import pickle
from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.internet import reactor, task
import sys
class ProtocolPacker:
    
    def pack(self, array):
        return pickle.dumps(array)
                        
    def unpack(self, data):
        try:
            unpacked = pickle.loads(data)
        except:
            unpacked = None
        return unpacked


class Server(DatagramProtocol):
    addresslist = []
    def removeclient(self, client):
        try:
            self.addresslist.remove(client)
            self.transport.write("OK", client)
            print "Client (IP: %s, Port: %s) Removed." % (client[0],client[1])
        except:
            pass
            
    def addclient(self, client):
        # Add the client to database
        if self.addresslist.count(client) == 0:
            self.addresslist.append(client)
            print "Client (IP: %s, Port: %s) Added." % (client[0],client[1])
            
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

class Client(DatagramProtocol):
    ip = '127.0.0.1'
    port = 9999
    recvcount = 0
    sentcount = 0
    debug = False
    started = False
    
    def connect(self, ip=ip, port=port):
        self.ip = ip
        self.port = port
        reactor.listenUDP(0, self)
        reactor.run()
        
    def disconnect(self):
        reactor.stop()
        
    def startProtocol(self):
        print "Protocol Started."
        self.started = True
        event_loop = task.LoopingCall(self.gameloop)
        event_loop.start(0.01, now=True)
        
    def printmsg(self):
        print "Got %s packets, sent %s packets, IP is %s and Port is %s.\r" % (self.recvcount, self.sentcount, self.ip, self.port) ,
        sys.stdout.flush()
        
    def datagramReceived(self, data, (host, port)):
        try:
            self.recvcount += 1
            if self.debug == True: self.printmsg()
            p = ProtocolPacker()
            if hasattr(self,): self.DataRecievedDecoded(p.unpack(data))
        except:
            pass
            
    def SendData(self, data=[]):
        self.sentcount += 1
        if self.debug == True: self.printmsg()
        p = ProtocolPacker()
        self.transport.write(p.pack(data), (self.ip, self.port))
