import math
import networkx as nx
import random
import numpy
import Queue
import time
import sys
import uuid
from threading import Thread, Lock
from time import sleep



class Mdigraph:
    #G is a MDG, L is the leaf nodes of the k-ary tree in the MDG.
    #S is the list of machines
    def __init__(self,G=None,L=None,S=None):
        self.G = G
        self.L = L

    def newnodekey(self):
        return str(uuid.uuid1())

class GraphGen:
    def draw(self,G,name="graph"):
        nx.nx_agraph.write_dot(G,name+".dot")

    def karytree(self,k=2,d=4):
        G = nx.balanced_tree(k,d)
        L = [] #Tree's leaves
        DiG = nx.DiGraph(G)
        n = len(G.nodes())
        down = n-int((math.pow(k,d)))
        L = list(range(down, n))
        return Mdigraph(DiG,L)

    def generatemachines(self,M):
        M.G.node[0]['key'] = '0'
        for i in range(1,len(M.G.nodes())):
            M.G.node[i]['key'] = M.newnodekey()

    def canonical(self,k=2,d=4):
        M = self.karytree(k,d)
        n = len(M.G.nodes())
        for l in M.L:
            M.G.add_edge(n,l)
        r=random.randint(0, len(M.L))
        M.G.add_edge(M.L[r],n)
        self.generatemachines(M)
        return M

    def levels(self,G,k,d):
        levels = [[0,0],[1,2]]
        #2 to d inclusive
        for i in range(2,d+1):
            N = int(math.pow(k,i))
            S = levels[-1][-1]
            nodes = list(range(S+1,S+N+1))
            levels.append(nodes)
        return levels


    def lastlevel(self,G,k,d): 
        N = int(math.pow(k,d)) #Size of last level
        target = len(G.nodes())-1
        return list(range(target-N,target)), target

class GraphUtil:
    def __init__(self):
        pass

    def ispathvalid(self,T,M):
        P = [n for n,k in T]
        try:
            #print 'Looking for ', P[0], ' up to ', P[len(P)-1], ' '
            #print 'Nodes: ', self.M.G.nodes()
            l,Q = nx.bidirectional_dijkstra(M.G,P[0],P[len(P)-1])
            print P,'->',Q

            #If the path exists in G, now check for correct keys
            if Q == P:
                for n,k in T:
                    if M.G.node[n]['key'] != k:
                        print 'Key mismatch: ', M.G.node[n]['key'], ' ', k
                        return False
                return True
        except Exception as e:
            return False

    def nextlevel(self,u,M):
        #This will give all the neighbors but
        #this includes those that are in a higher level.
        #We'll remove nodes that have lower indexes.
        L = M.G.neighbors(u)
        for n in L:
            if n < u:
                L.remove(n)
        return L

    def nextlevelwithkeys(self,u,M):
        #This will give all the neighbors but
        #this includes those that are in a higher level.
        #We'll remove nodes that have lower indexes.
        L = M.G.neighbors(u[0]) #List of nodes
        K = [] #List of nodes and keys
        for n in L:
            if n < u[0]:
                L.remove(n)
        for n in L:
            K.append((n,M.G.node[n]['key']))
        return K
