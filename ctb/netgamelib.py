import pickle
from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.internet import reactor, task
import sys
import time
import zlib

version = 3.0
LOOPSPEED = 0.01

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
            
class Events():
    """
    Events to put in game
    """
    def data_recieved(self, data, rawdata, client):
        """
        Recieved Data Event.
        Client + Server
        """
        pass
    def game_loop(self):
        """
        Main game loop for server side physics for example.
        Client + Server
        """
        pass
    def connected(self):
        """
        Run when server started
        Client + Server
        """
        pass
    def new_client(self, client):
        """
        Event for when a new client has connected.
        Server
        """
        pass
    def server_shutdown(self):
        """
        Run when protocol is shut down
        Server
        """
        pass
    def client_disconnect(self, client):
        """
        Event for when a new client disconnects.
        Server
        """
        pass
    def client_shutdown(self):
        """
        Run when protocol is shut down
        Client
        """
        pass 
           
class Server(DatagramProtocol, DebugStuff, Events):
    """
    Inherit this server class to use it.
    Use instance.listen() to start it.
    """
    addresslist = []
    protocolclass = ProtocolPacker
    
    def listen(self,port):
        """
        Start listening for connections.
        """
        reactor.listenUDP(port, self)
        reactor.run()
        
    def remove_client(self, client):
        """
        Remove a client
        """
        try:
            self.addresslist.remove(self.find_client(client))
            print "Client (IP: %s, Port: %s) Removed." % (client[0],client[1])
            self.client_disconnect(client)
            return True
        except:
            return False
        
    def find_client(self, client):
        """
        Find client in addresslist from a IP, PORT tuple
        Else return None
        """
        for item in self.addresslist:
            if item['ip'] == client:
                return item
        return None
        
    def find_addresslist_id(self, client):
        """
        Find the id number in addresslist array from a IP, PORT tuple
        Else return None
        """
        result = 0
        for item in self.addresslist:
            if item['ip'] == client:
                return result
            result += 1
        return None
        
    def list_clients(self):
        """
        Returns self.addresslist, makes code look tidy.
        """
        return self.addresslist
    
    def add_client(self, client):
        """
        Add the client to database
        """
        if self.find_client(client) == None:
            self.addresslist.append({'ip' : client, 
                                    'uid': zlib.crc32(str(client)),
                                    'timestamp': time.time(),
                                    'connecttimestamp': time.time()})
            print "Client (IP: %s, Port: %s) Added." % (client[0],client[1])
            
    def disconnect_idle_clients(self, idlewait):
        """
        Disconnect any idle clients based on
        time elapsed since the timestamp.
        idlewait is the time to wait before
        disconnecting in seconds.
        """
        for item in self.addresslist:
            now = time.time()
            timestamp = item['timestamp']
            if now - timestamp > idlewait:
                self.removeclient(item['ip'])
                
    def send_to_one(self, data, client):
        """
        Send message to one person.
        """
        p = self.protocolclass()
        self.transport.write(p.pack(data), client)
        self.inc('sent')
        
    def send_to_all(self, data, client = None, excludeself = True):
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
        """
        Packet recieved event from twisted
        """
        p = self.protocolclass()
        pdata = p.unpack(data)
        client = (host, port)
        clientid = self.find_addresslist_id(client)
        self.addresslist[clientid]['timestamp'] = time.time()
        self.inc("recv")
        self.add_client(client)
        self.data_recieved(pdata,data,client)
        
    def startProtocol(self):
        """
        Twisted protocol started
        """
        self.connected()
        event_loop = task.LoopingCall(self.game_loop)
        event_loop.start(LOOPSPEED, now=True)
        
    def stopProtocol(self):
        """
        Twisted protocol stopped
        """
        self.server_shutdown()
        
class Client(DatagramProtocol, DebugStuff, Events):
    """
    Inherit this client class to use it.
    Use instance.connect() to start it.
    """
    ip = '127.0.0.1'
    port = 9999
    started = False
    protocolclass = ProtocolPacker
    
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
        """
        Twisted protocol started
        """
        print "Protocol Started."
        self.started = True
        self.connected()
        event_loop = task.LoopingCall(self.game_loop)
        event_loop.start(LOOPSPEED, now=True)
        
    def stopProtocol(self):
        """
        Twisted protocol stopped
        """
        self.client_shutdown()
        
    def datagramReceived(self, data, (host, port)):
        """
        Packet recieved event from twisted
        """
        p = self.protocolclass()
        client = (host, port)
        self.inc('recv')
        self.data_recieved(p.unpack(data), data, client)

    def send_data(self, data=[]):
        """
        Send data to a client.
        """
        self.inc('sent')
        p = self.protocolclass()
        self.transport.write(p.pack(data), (self.ip, self.port))
        
    def find_client(self, client, addresslist):
        """
        Find client in addresslist from a IP, PORT tuple
        """
        for item in addresslist:
            if item['ip'] == client:
                return item
