from random import randrange, choice
import Queue
from CheckpointController import CpHandler
from Message import CheckpointMessage
import threading
import socket
import commands
import select

class Communicator:


    def __init__(self, cmdArgs):

        self.inChannel = {}
        self.outChannel = {}

        self.totalSegs = cmdArgs["numSegs"]
        self.totalProcs = cmdArgs["numProcs"]
        self.peers = cmdArgs["peers"]
	self.incomingPeers = [(x[0],int(x[1])) for x in self.peers]
        self.me =  commands.getoutput("hostname -I").strip()


        self.connections = dict((_id,host) for _id,host in enumerate(self.peers))


        self.procId = None
        # remove self from the coneections
        # and updating procId

        for procId in self.connections:
            if self.connections[procId][0].strip() == self.me:
                self.procId = procId
                self.meComplete = self.connections[procId]
                del self.connections[procId]
                break

        print "me : " , self.meComplete
        print "connected items :"
        for p in self.connections.items():
            print p

        
        assert(len(self.connections.keys()) == len(self.peers)-1)
        self.numPeers = len(self.connections.keys())


        self.ckptCntrl = CpHandler(self.procId, self.totalProcs)

        tOut = threading.Thread(target=self._setupOutChannels)
        tIn = threading.Thread(target=self._setupInChannels)

        #tOut.start()
        tIn.start()
        tOut.start()
        tOut.join()
        tIn.join()
	exit()


    def _setupOutChannels(self):

	keys = self.connections.keys()
	peerCounter = 0
	while peerCounter < len(keys):
	    _id = keys[peerCounter]	
            #for _id in self.connections:
            peer = self.connections[_id]
            peerIp = peer[0]
            peerSendPort = peer[1]
            peerRecvPort = peer[2]
            
            
	    soc = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            soc.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	    soc.bind(('',self.meComplete[1]))

            # Ipv4 with TCP connection
            soc.settimeout(5.0)

            try:
                soc.connect((peerIp, peerRecvPort))

            except socket.timeout:

                print "Timeout issue"
                raise SystemExit(0)
	    
	    except:
		peerCounter-=1
	
	    peerCounter+=1 
		


    def _setupInChannels(self):

        self.recvSoc = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        # Ipv4 with TCP connection

        self.recvSoc.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        self.recvSoc.bind(( '', self.meComplete[2] ))
        self.recvSoc.listen(self.numPeers)
	
        print "Listening at ", socket.gethostname(), " : ", self.meComplete

        for _ in self.peers:
            (client,addr) = self.recvSoc.accept()
            print "Received connection from " , addr
            self.inChannel[self.incomingPeers.index(addr)] = client


    def getMyId(self):

        return self.procId

    def getNumSegs(self):

        return self.totalSegs

    def _send(self, message, dest):
        message = pickle.dump(message)
        self.outChannel[dest].send(message)

    def _receive(self, fromChannel):
        message = fromChannel.recv()
        message = pickle.loads(message)

        if isinstance(message,CheckpointMessage):
            self.ckptCntrl.handleRequests(message)
            return None

        if self.ckptCntrl.messageConsumptionAllowed(recvdMsg):
            #consume the message
            return recvdMsg

        return None


    def trySendingCp(self):
        if self.ckptCntrl.checkpointInitAllowed():
            for msg in self.ckptCntrl.checkpointInit():
                self._send(msg, dest=msg.receiver)

    def send(self, toProc, message):
        self.trySendingCp()
        message.setBB(self.ckptCntrl.cpEnabled and self.ckptCntrl.cpTaken)
        self._send(message,dest=toProc)


    def sendToRandom(self, message):

        self.send(randrange(self.totalProcs), message)

    def getNonEmptyChannels(self):

        readable, writable, error = select.select([x[0] for x in self.inChannel.values()],[],[])
        return readable

    def nonBlockingReceive(self):

        self.trySendingCp()

        nonEmptyChannels = self.getNonEmptyChannels()
        if nonEmptyChannels:
            return self._receive(choice(nonEmptyChannels))
        return None
