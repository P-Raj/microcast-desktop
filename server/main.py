
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import os
import simplejson
import math

MaxSegmentSize = 10


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
        for segId in range(math.floor(size/MaxSegmentSize))

    def parsePath(self):
        args = dict(
            (tuple(arg.split('='))
                for arg in self.path[1:].split("&")))
        return args

    def do_GET(self):

        self.args = parsePath()
        if "request" in self.args:
            content = self.getContent(self.args["file"],
                                      self.args["start"], self.args["end"])
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(content)

        elif "init" in self.args:
            meta = self.getSegmentMeta(filename)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(simplejson.dump(meta))

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
