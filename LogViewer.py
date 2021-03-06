import LogStore
import getopt
import sys


def readCmdArgs():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:", ["process"])

    except getopt.GetoptError:
        print sys.argv[0] + "-h (for help)"
        sys.exit(2)

    processes = []

    for opt, arg in opts:
        if opt == "-h":
            print "python LogViewer.py [-p proc1,proc2..]"
            sys.exit()
        elif opt in ("-p", "--process"):
            processes = map(int, arg.split(","))
    return processes

maxLen = 0
lineNum = 0


def getProcLog(data):
    global maxLen
    string = "P" + str(data["procId"]) + "." + \
        data["op"] + " " + str(data.get("queue", '')) + \
        " " + str(data.get("message", ""))
    maxLen = max(maxLen, len(string))
    return data["procId"], string


def getChanLog(dict):
    global maxLen
    string = "C" + str(dict["from"]) + str(dict["to"]) + \
        "." + dict["op"] + "(" + str(dict["message"]) + ")"
    maxLen = max(maxLen, len(string))
    if "receive" in dict["op"]:
        return dict["to"], string
    return dict["from"], string


def printTerminal(data):

    if data["type"] == "process":
        printData = getProcLog(data)
    elif data["type"] == "channel":
        printData = getChanLog(data)

    sys.stdout.write("%s %s \n" % (printData[0]*20*" ", printData[1]))
    sys.stdout.flush()


if __name__ == "__main__":

    processes = readCmdArgs()
    datas = []
    #LogStore.readLog()
    printData = []
    for data in datas:
        if data["type"] == "process":
            if data["procId"] in processes:
                printData.append(getProcLog(data))
        elif data["type"] == "channel":
            if data["from"] in processes and data["to"] in processes:
                printData.append(getChanLog(data))

    for data in printData:
        print data[0]*(maxLen+2)*" ", data[1]
