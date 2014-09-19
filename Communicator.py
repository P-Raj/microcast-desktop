from random import randrange, choice
import Queue
from CheckpointController import CpHandler
from Message import CheckpointMessage
import threading
import socket
import commands
import select
import pickle
import json

class Communicator:


    def __init__(self, cmdArgs):

        self.inChannel = {}
        self.outChannel = {}

	self.rec = Queue.Queue()
	
        self.totalProcs = cmdArgs["numProcs"]
        self.peers = cmdArgs["peers"]
	self.incomingPeers = [(x[0],int(x[1])) for x in self.peers]
	self.outgoingPeers = [(x[0],int(x[2])) for x in self.peers]
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
	# connections established


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
		print "[OUT] connected to", (peerIp,peerRecvPort)
	        peerCounter+=1 
		self.outChannel[self.outgoingPeers.index((peerIp,peerRecvPort))] = soc
		#self.incomingPeers.index((peerIp,peerRecvPort))] = soc

            except socket.timeout:

                print "Timeout issue"
                raise SystemExit(0)

	    
	    except:
		pass	
		
	print "[OUT] connections established"
	print self.outChannel

    def _setupInChannels(self):

        self.recvSoc = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        # Ipv4 with TCP connection

        self.recvSoc.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        self.recvSoc.bind(( '', self.meComplete[2] ))
        self.recvSoc.listen(self.numPeers)

        print "Listening at ", socket.gethostname(), " : ", self.meComplete

        for _ in range(len(self.peers)-1):
            (client,addr) = self.recvSoc.accept()
            print "Received connection from " , addr
            self.inChannel[self.incomingPeers.index(addr)] = client

	print "All incoming channels established"
	for soc in self.inChannel.values():
		t = threading.Thread(target=self.readlines, args=[soc])
		t.start()


    def getMyId(self):

        return self.procId

    def _send(self, message, dest):
        print "Sending message" , message, "to ", dest, " ",	

        message = pickle.dumps(message)

	#sending length
	message_length = len(message)

	self.outChannel[dest].send('<MESSAGELENGTH>%s</MESSAGELENGTH>' %str(message_length))

	for message_i in range(0,message_length,1024):
		self.outChannel[dest].send(message[:1024])
		message = message[1024:]
        

    def _receive(self):

	if self.rec.empty():
		return None
	
        message = self.rec.get()

        if isinstance(message,CheckpointMessage):
            self.ckptCntrl.handleRequests(message)
            return None

        if self.ckptCntrl.messageConsumptionAllowed(message):
            #consume the message
            return message

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

        readable, writable, error = select.select([x for x in self.inChannel.values()],[],[])
        return readable

    def nonBlockingReceive(self):

        self.trySendingCp()

        nonEmptyChannels = self.getNonEmptyChannels()
        if nonEmptyChannels:
            return self._receive(choice(nonEmptyChannels))
        return None

    def readlines(self, sock, recv_buffer=4096):

	buffer = ''
	data  = True
	lines = []
	item = ''
	firstRun = True

	while True:
		msg = ''
		while '<MESSAGELENGTH>' not in msg and '</MESSAGELENGTH>' not in msg:
			msg = sock.recv(1024)
		msglen = int(msg.split('</MESSAGELENGTH>')[0].split('<MESSAGELENGTH>')[1])
		msg = msg.split('</MESSAGELENGTH>')[1]

		while len(msg) < msglen:
			msg += sock.recv(msglen-len(msg))

		assert(len(msg) == msglen)
		
		self.rec.put(pickle.loads(msg))
	return
