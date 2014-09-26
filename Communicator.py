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

        self.totalProcs = cmdArgs["numProcs"]
        self.peers = cmdArgs["peers"]
        
        self.terminate = False
        self.readingThreads = []
	self.readLock = threading.Lock()

        self.inPeers = [(x[0], int(x[1])) for x in self.peers]
        self.outPeers = [(x[0], int(x[2])) for x in self.peers]

        self.setChannels()
        self.printChannels()

        self.sendLock = threading.Lock()

        assert(len(self.connections.keys()) == len(self.peers)-1)

        self.numPeers = len(self.connections.keys())

        self.ckptCntrl = CpHandler(self.procId, self.totalProcs)

        try:
            self.start()
        except KeyboardInterrupt:
            print "Interrupted by user"
            print "Closing open sockets..."
            self.close()
            print "done"

    def start(self):

        tOut = threading.Thread(target=self.enableOutChan)
        tIn = threading.Thread(target=self.enableInChan)
        tIn.start()
        tOut.start()
        tOut.join()
        tIn.join()

    def close(self):

        print "closing the communicaor object"
        
        self.readLock.acquire()
        self.terminate = True
        self.readLock.release()
        
        for readers in self.readingThreads:
            readers.join()
        print "Closed Reading threads"

        for openSockets in self.outChan.values() + self.inChan.values():
            openSockets.shutdown(socket.SHUT_RDWR)
        print "Closed Open Sockets"

    def setChannels(self):

        self.rec = Queue.Queue()
        self.inChan = dict()
        self.outChan = dict()

        self.inPeers = [(x[0], int(x[1])) for x in self.peers]
        self.outPeers = [(x[0], int(x[2])) for x in self.peers]

        self.me = commands.getoutput("hostname -I").strip()
        self.meComplete = None

        self.connections = dict((_id, host)
                                for _id, host in enumerate(self.peers))

        self.procId = None

        # remove self from the coneections
        # and updating procId

        for procId in self.connections:
            if self.connections[procId][0].strip() == self.me:
                self.procId = procId
                self.meComplete = self.connections[procId]
                del self.connections[procId]
                break

        if not self.meComplete:
            raise Exception("The system is not a part of the cluster")
            exit(1)

    def printChannels(self):

        print "System : ", self.meComplete
        print "Peers :"
        for _id in sorted(self.connections.keys()):
            print _id, ". ", self.connections[_id]

    def enableOutChan(self):

        keys = self.connections.keys()

        peerCounter = 0

        while peerCounter < len(keys):

            _id = keys[peerCounter]
            peer = self.connections[_id]

            peerIp, peerSendPort, peerRecvPort = peer[:3]

            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            soc.bind(('', self.meComplete[1]))

            # Ipv4 with TCP connection
            soc.settimeout(5.0)
            #soc.setblocking(1)

            try:
                soc.connect((peerIp, peerRecvPort))
                peerCounter += 1
                self.outChan[self.outPeers.index((peerIp, peerRecvPort))] = soc
                print "[OUT] connected to", (peerIp, peerRecvPort)

            except socket.timeout:
                print "Timeout issue"
                raise SystemExit(0)

            except:
                pass

        print "[OUT] connections established"

        for i, chan in enumerate(self.outChan.keys()):
            print i, ". ", chan

    def enableInChan(self):

        self.recvSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Ipv4 with TCP connection

        self.recvSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.recvSoc.bind(('', self.meComplete[2]))
        self.recvSoc.listen(self.numPeers)

        print "Listening at ", socket.gethostname(), " : ", self.meComplete

        for _ in range(len(self.peers)-1):
            (client, addr) = self.recvSoc.accept()
            print "Received connection from ", addr
            self.inChan[self.inPeers.index(addr)] = client

        print "[IN] connections established"

        for soc in self.inChan.values():
            self.readingThreads.append(threading.Thread(target=self.readlines, args=[soc]))
            self.readingThreads[-1].start()

    def getMyId(self):

        return self.procId

    def _send(self, message, dest):

        self.sendLock.acquire()
        message = pickle.dumps(message)
        #sending length
        message_length = len(message)
        self.outChan[dest].send('<MESSAGELENGTH>%s</MESSAGELENGTH>'
                                % str(message_length))

        for message_i in range(0, message_length, 1024):
            self.outChan[dest].send(message[:1024])
            message = message[1024:]

        self.sendLock.release()

    def _receive(self):

        if self.rec.empty():
            return None

        message = self.rec.get()

        if isinstance(message, CheckpointMessage):
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
        self._send(message, dest=toProc)

    def sendToRandom(self, message):

        self.send(randrange(self.totalProcs), message)

    def getNonEmptyChannels(self):

        readable, writable, error = select.select(
            [x for x in self.inChan.values()], [], [])
        return readable

    def nonBlockingReceive(self):

        self.trySendingCp()

        nonEmptyChannels = self.getNonEmptyChannels()
        if nonEmptyChannels:
            return self._receive(choice(nonEmptyChannels))

        return None

    def readlines(self, sock):

        while True:

            self.readLock.acquire()

            if self.terminate:
                break

            msg = '' # initialize outside since otherwise remiander of previous message would be lost
            
            opTag = '<MESSAGELENGTH>' # no need to repeat this in each iteration
            clTag = '</MESSAGELENGTH>' # no need to repeat this in each iteration

            while True:
                while not all(tag in msg for tag in (opTag, clTag)):
                    msg += sock.recv(1024) # += rather than =
                msglen = int(msg.split(clTag)[0].split(opTag)[1])
                msg = msg.split(clTag, 1)[1] # split just once, starting from the left
                while len(msg) < msglen:
                    msg += sock.recv(msglen-len(msg))
                self.rec.put(pickle.loads(msg[:msglen])) # handle just one message
                msg = msg[msglen:] # prepare for handling future messages

            self.readLock.release()

        return
