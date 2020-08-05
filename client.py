import netgamelib, signal
print "NetGameLib Verson", netgamelib.version
class Game(netgamelib.Client):
    def Connected(self):
        self.SendData("list")
    def DataRecieved(self, data, rawdata, client):
        print "Recieved", data
        
mygame = Game()
def handler(signum, frame):
    mygame.SendData("disconnect")
    mygame.disconnect()
signal.signal(signal.SIGINT, handler)
mygame.connect(ip='127.0.0.1',port=9999)    
