
'''
This is a graph randomizer which switches edges and resets nodes on the two ends of the switched edge.

'''

from time import sleep
from threading import Lock
from mdg import GraphUtil,GraphGen
import random

class Randomizer:
    def __init__(self):
        self.gu = GraphUtil()
        self.gg = GraphGen()
        self.rand_stop = False

    #Find the link to target.
    def whohaslinktotarget(self,M):
        last,target = self.gg.lastlevel(M.G,k,d)
        hasit = -1
        for u in last:
            if (u,target) in M.G.edges():
                hasit = u
        return hasit,last,target

    #Find a replacement to be linked to target.
    def linktotarget(self):
        hasit,last,target = self.whohaslinktotarget(M)
        replacement = last[random.randint(0,len(last)-1)]
        if replacement == hasit or hasit == -1:
            return None,None,None
        return hasit,replacement,target

    #Find two pairs of edges to switch. The switch is done in
    #another function.
    def twopairsofedges(self,M,levels):

        #Pick a level
        level = levels[random.randint(0,len(levels)-2)]

        #if it's level 0, a different treatment
        if level[0] == 0:
            u = 0
            w = 0
        else:
            u = random.randint(level[0], level[len(level)-1] )
            #Pick two nodes in level
            R = range(level[0], u) + range(u,level[len(level)-1])
            w = random.choice(R)

        #print 'Chosen: ', u, ' and ', w

        #Pick a next level node connected to u and w
        N = len(self.gu.nextlevel(u,M))
        v = self.gu.nextlevel(u,M)[random.randint(0,N-1)]
        x = self.gu.nextlevel(w,M)[random.randint(0,N-1)]

        #Switch and return
        return [(u,v),(w,x)],[(u,x),(w,v)]

    #Switches all the nodes in the set of pairs A
    #which are about to be switched
    def resetmachines(self,M,A):
        for u,v in A:
            #print M.G.node[u]['key'], ' switched to ',
            #To make it easier for the attacker to find node 0. Otherwise, the simulation will be a lot more complicated.
            if u != 0:
                M.G.node[u]['key'] = M.newnodekey()
            #print M.G.node[u]['key'], ' :-)'

    #Switch the edges
    #No changes in link to target for now.
    def edgeSwitcher(self,M,levels,mutex,switch_rate):
        #Pick two pairs of edges and swipe them!
        while not self.rand_stop:
            A,S = self.twopairsofedges(M,levels)
            if A is False:
                continue
            mutex.acquire()
            self.resetmachines(M,A)
            M.G.remove_edges_from(A)
            M.G.add_edges_from(S)
            mutex.release()
            #print 'Edge switch complete from ',A, ' to ',S

            # hasit,replacement,target = self.linktotarget()
            # if replacement is not None:
            #     #print "New node to target: ", replacement, ' replacing ', hasit
            #     mutex.acquire()
            #     M.G.remove_edges_from([(hasit,target)])
            #     M.G.add_edges_from([(replacement,target)])
            #     mutex.release()
            sleep(switch_rate)

    #Fixed number of switches
    def edgeSwitcherFixed(self,M,levels,mutex,no_switches):
        #Pick two pairs of edges and swipe them!
        for i in range(0,no_switches):
            A,S = self.twopairsofedges(M,levels)
            if A is False:
                continue
            mutex.acquire()
            self.resetmachines(M,A)
            M.G.remove_edges_from(A)
            M.G.add_edges_from(S)
            print A, ' switch: ', S
            mutex.release()
