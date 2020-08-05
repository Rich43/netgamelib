import pickle
from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.internet import reactor, task
import sys
import time
import zlib

version = 2.0

class ProtocolPacker:
    def pack(self, array):
        return pickle.dumps(array)
                        
    def unpack(self, data):
        try:
            unpacked = pickle.loads(data)
        except:
            unpacked = None
        return unpacked

class DebugStuff:
    recvcount = 0
    sentcount = 0
    debug = False
    def inc(self,type):
        def printmsg(self):
            print "Got %s packets, sent %s packets.\r" \
             % (self.recvcount, self.sentcount) ,
            sys.stdout.flush()
        if type == 'sent':
            self.sentcount += 1
        if type == 'recv':
            self.recvcount += 1
        if self.debug == True:
            printmsg()
            
class Server(DatagramProtocol, DebugStuff):
    addresslist = []
    protocolclass = ProtocolPacker
    
    # Events to put in game
    def DataRecieved(self, data, rawdata, client):
        """
        Recieved Data Event.
        """
        pass
    def gameloop(self):
        """
        Main game loop for server side physics for example.
        """
        pass
    def newclient(self, client):
        """
        Event for when a new client has connected.
        """
        pass
    def clientdisconnect(self, client):
        """
        Event for when a new client disconnects.
        """
        pass
    def servershutdown(self):
        """
        Run when protocol is shut down
        """
        pass
    def Connected(self):
        """
        Run when server started
        """
        pass
    
    # Functions
    def listen(self,port):
        """
        Start listening for connections.
        """
        reactor.listenUDP(port, self)
        reactor.run()
        
    def removeclient(self, client):
        """
        Remove a client
        """
        try:
            self.addresslist.remove(self.findclient(client))
            print "Client (IP: %s, Port: %s) Removed." % (client[0],client[1])
            self.clientdisconnect(client)
            return True
        except:
            return False
        
    def findclient(self, client):
        """
        Find client in addresslist from a IP, PORT tuple
        Else return None
        """
        for item in self.addresslist:
            if item['ip'] == client:
                return item
        return None
    
    def listclients(self):
        """
        Returns self.addresslist, makes code look tidy.
        """
        return self.addresslist
    
    def addclient(self, client):
        """
        Add the client to database
        """
        if self.findclient(client) == None:
            self.addresslist.append({'ip' : client, 
                                    'uid': zlib.crc32(str(client))})
            print "Client (IP: %s, Port: %s) Added." % (client[0],client[1])
            
    def sendtoone(self, data, client):
        """
        Send message to one person.
        """
        p = self.protocolclass()
        self.transport.write(p.pack(data), client)
        self.inc('sent')
        
    def sendtoall(self, data, client = None, excludeself = True):
        """
        Send message to all clients.
        Set excludeself to False to send to yourself also.
        """
        p = self.protocolclass()
        for listclient in self.addresslist:
            if listclient['ip'] != client and excludeself == True:
                self.transport.write(p.pack(data), listclient['ip'])
                self.inc('sent')
                continue
            if excludeself == False:
                self.transport.write(p.pack(data), listclient['ip'])
                self.inc('sent')
                continue
            
    def disconnect(self):
        """
        Shutdown the server
        """
        reactor.stop()
        
    def datagramReceived(self, data, (host, port)):
        p = self.protocolclass()
        pdata = p.unpack(data)
        client = (host, port)

        self.addclient(client)
        self.DataRecieved(pdata,data,client)
        
    def startProtocol(self):
        self.Connected()
        event_loop = task.LoopingCall(self.gameloop)
        event_loop.start(0.01, now=True)
        
    def stopProtocol(self):
        self.servershutdown()
        
class Client(DatagramProtocol, DebugStuff):
    ip = '127.0.0.1'
    port = 9999
    started = False
    protocolclass = ProtocolPacker
    
    # Events to put in game
    def gameloop(self):
        """
        Game Loop Event
        """
        pass
    def DataRecieved(self, data, rawdata, client):
        """
        Recieved data event
        """
        pass
    def Connected(self):
        """
        Connected to server event
        """
        pass
    def clientshutdown(self):
        """
        Run when protocol is shut down
        """
        pass
    # Other functions
    def connect(self, ip=ip, port=port):
        """
        Connect to a server
        """
        self.ip = ip
        self.port = port
        reactor.listenUDP(0, self)
        reactor.run()
        
    def disconnect(self):
        """
        Disconnect from a server
        """
        reactor.stop()
        
    def startProtocol(self):
        print "Protocol Started."
        self.started = True
        self.Connected()
        event_loop = task.LoopingCall(self.gameloop)
        event_loop.start(0.01, now=True)
        
    def stopProtocol(self):
        self.clientshutdown()
        
    def datagramReceived(self, data, (host, port)):
        p = self.protocolclass()
        client = (host, port)
        self.inc('recv')
        self.DataRecieved(p.unpack(data), data, client)

    def SendData(self, data=[]):
        """
        Send data to a client.
        """
        self.inc('sent')
        p = self.protocolclass()
        self.transport.write(p.pack(data), (self.ip, self.port))
        
    def findclient(self, client, addresslist):
        """
        Find client in addresslist from a IP, PORT tuple
        """
        for item in addresslist:
            if item['ip'] == client:
                return item