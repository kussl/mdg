'''
This server program handles both D and r paramters. For every request, it performs ceil(r/D) switches before assessing whether a path sent by the attacker is valid or not. Thus, the attacker has zero delay and sequentially sends requests to the server.
'''
from cloud.mdg import Mdigraph,GraphGen,GraphUtil
from cloud.randomizer import Randomizer
from threading import Thread, Lock
from time import sleep
import random
import SocketServer
import sys
import getopt
import ast
import math

k=2
d=4
gg = GraphGen()
M = gg.canonical(k=k,d=d)
gu = GraphUtil()
gg.draw(M.G)
levels = gg.levels(M.G,k,d)

D=0.2
r=0.05
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
            randomizer(int(math.floor(D/r)))
            mutex.acquire()
            if gu.ispathvalid(trajectory,M):
                answer = gu.nextlevelwithkeys(trajectory[len(trajectory)-1],M)
                print 'Next: ', answer
            mutex.release()
            self.request.sendall(str(answer)+"\n")


def randomizer(no_switches=2):
    R = Randomizer()
    R.edgeSwitcherFixed(M,levels,mutex,no_switches)

def should_stop(server):
    terminate = ""
    while "yes" not in terminate:
        terminate = raw_input("Should I stop? ")
    rand_stop = True
    server.shutdown()
    server.server_close()

def runcloud(port=9999,D=0.1,r=0.05):
    HOST, PORT = "localhost", port
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    thread = Thread(target = should_stop, args = (server,))
    thread.start()

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
    runcloud(port,D,r)

if __name__ == "__main__":
    main()
