
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import os
import json
import math

MaxSegmentSize = 100000


class FileHandler(BaseHTTPRequestHandler):

    def getContent(self, filename, startByte):
        with open(filename, "rb") as fp:
            fp.seek(startByte)
            data = fp.read(MaxSegmentSize)
        return data

    def getFileSize(self, filename):
        size = 0
        with open(filename, "rb") as fp:
            fp.seek(0, 2)
            size = fp.tell()
        return size

    def getSegmentMeta(self, filename):
        size = self.getFileSize(filename)
        meta = {}
        meta["size"] = size
        meta["Segments"] = {}
        for segId in range(size/MaxSegmentSize):
            meta["Segments"][segId] = MaxSegmentSize*segId
        return meta

    def parsePath(self):
        args = dict(
            (tuple(arg.split('='))
                for arg in self.path[1:].split("&")))
        return args

    def do_GET(self):

        self.args = self.parsePath()
        if "request" in self.args:
            content = self.getContent(self.args["file"],
                                      int(self.args["start"]))
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(content)

        elif "init" in self.args:
            meta = self.getSegmentMeta(self.args["file"])
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(meta))

        else:
            raise Exception("Unknown request")


if __name__ == "__main__":

    server = HTTPServer(('', 8888), FileHandler)
    print "Staring server"
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "Server stopped because of keyboard interrupt"
        server.socket.close()
