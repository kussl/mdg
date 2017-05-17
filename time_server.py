
from cloud.mdg import Mdigraph,GraphGen,GraphUtil
from cloud.randomizer import Randomizer
from threading import Thread, Lock
from time import sleep
import random
import SocketServer
import sys
import getopt
import ast

k=2
d=4
gg = GraphGen()
M = gg.canonical(k=k,d=d)
gu = GraphUtil()
gg.draw(M.G)
levels = gg.levels(M.G,k,d)

switch_rate = 0.01 #Rate by which the misery digraph is randomized.
inference_rate = 0 #switch_rate/2 #Rate by which next level is inferred.

#For accessing the graph, required when
#graph randomization is in place.
mutex = Lock()


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = ""
        while("endit" not in self.data):
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()
            if not self.data:
                break
            print "{} wrote:".format(self.client_address[0])
            print self.data

            trajectory = ast.literal_eval(self.data)
            answer = []
            mutex.acquire()
            if gu.ispathvalid(trajectory,M):
                sleep(inference_rate)
                answer = gu.nextlevelwithkeys(trajectory[len(trajectory)-1],M)
                print 'Next: ', answer
            mutex.release()
            self.request.sendall(str(answer)+"\n")


def should_stop(server):
    terminate = ""
    while "yes" not in terminate:
        terminate = raw_input("Should I stop? ")
    rand_stop = True
    server.shutdown()
    server.server_close()

def randomizer():
    R = Randomizer()
    R.edgeSwitcher(M,levels,mutex,switch_rate)


def runcloud(port=9999,switch=True):
    HOST, PORT = "localhost", port
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    thread = Thread(target = should_stop, args = (server,))
    thread.start()

    #Do the edge switch or not?
    if switch:
        print 'Randomizing'

        randomizer_thread = Thread(target = randomizer)
        randomizer_thread.start()


def main():
    port = 9999
    switch = True
    optlist, args = getopt.getopt(sys.argv[1:], 'p:s:')

    p,givenport = optlist[0]
    if len(givenport)>0:
        port = int(givenport)
    s,givenswitch = optlist[1]
    if givenswitch == "false":
        switch = False
    runcloud(port,switch)

if __name__ == "__main__":
    main()
