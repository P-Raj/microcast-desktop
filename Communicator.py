from random import randrange, choice
import Queue
from CheckpointController import CpHandler
from Message import CheckpointMessage
import threading

class Communicator:


    def __init__(self, cmdArgs):

        self.inChannel = {}
        self.outChannel = {}

        self.totalSegs = cmdArgs["numSegs"]
        self.totalProcs = cmdArgs["numProcs"]
        self.peers = cmdArgs["peers"]
        self.me = socket.gethostname()

        self.connections = dict((_id,host) for _id,host in enumerate(self.peers))

        self.procId = None
        # remove self from the coneections
        # and updating procId
        for procId in self.connections:
            if self.connections[procId] == self.me:
                self.connections.remove(procId)
                break

        assert(len(self.connections.keys()) == len(self.peers)-1)

        self.sendPort = 8080
        self.recvPort = 8081

        self.ckptCntrl = CpHandler(self.procId, self.totalProc)

        tOut = threading.Thread(target=self._setupOutChannels)
        tIn = threading.Thread(target=self._setupInChannels)

        tOut.start()
        tIn.start()

        tOut.join()
        tIn.join()


    def _setupOutChannels(self):

        for _id in self.connections:

            peer = self.connections[_id]

            soc = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            # Ipv4 with TCP connection
            soc.bind(('', self.sendPort))
            soc.settimeout(5.0)

            try:
                soc.connect((peer, self.recvPort))

            except socket.timeout:

                print "Timeout issue"
                raise SystemExit(0)

            self.outChannel[_id] = soc


    def _setupInChannels(self):

        self.recvSoc = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        # Ipv4 with TCP connection

        self.recvSoc.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        self.recvSoc.bind(( '', self.recvPort ))
        self.recvSoc.listen(self.numPeers)

        for _ in self.peers:
            (client,addr) = self.recvSoc.accept()
            print "Received connection from " , addr
            self.inChannel[self.peers.index(addr)] = client


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

        self.send(randrange(self.totalProc), message)

    def getNonEmptyChannels(self):

        readable, writable, error = select.select([x[0] for x in inChannel.values()],[],[])
        return readable

    def nonBlockingReceive(self):

        self.trySendingCp()

        nonEmptyChannels = self.getNonEmptyChannels()
        if nonEmptyChannels:
            return self._receive(choice(nonEmptyChannels))
        return None
