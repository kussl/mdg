
import socket
import sys
import ast
import networkx as nx
import random
import datetime
import numpy as np
import os
from threading import Thread
from time import sleep

targetnode = 31

class Attack:
	def __init__(self, port=9999, delay=1, loc="data"):
		self.delay = delay
		self.port = port
		self.silent = True
		self.dataloc = loc
		pass

	def talktocloud(self,T):
		HOST, PORT = "localhost", self.port
		#data = (str(T))[1:-1].replace(" ", "")
		data = str(T)

		# Create a socket (SOCK_STREAM means a TCP socket)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			# Connect to server and send data
			sock.connect((HOST, PORT))
			sock.sendall(data + "\n")
			#print data, ' sent'

			# Receive data from the server and shut down
			received = sock.recv(1024)
		finally:
		    sock.close()

		return ast.literal_eval(received)

	def compromise(self, u):
		sleep(self.delay)
		return True

	def addnexttograph(self,G,u,L):
		for v,k in L:
			G.add_edge(u,v)
			G.node[v]['key'] = k
		return G

	def removepathfromgraph(self,G,P):
		print P
		for i,u in enumerate(P):
			if i == len(P)-1:
				break
			G.remove_edge(u,P[i+1])
		return G

	def terminationreport(self,D,done=True):
		if not self.silent:
			print('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
			if done:
				print "I'm done!"
			else:
				print "I'm sorry, but the server cut me loose! :("
			print 'Trajectory: ', D
			print 'Length: ', len(D)

	def announcestart(self):
		if not self.silent:
			print 'Attacking...'
			print('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

	def pickanodetoinvade(self,L,D):
		i = random.randint(0,len(L)-1)
		U = L[i]
		D.append(U)
		#print 'Chose ', U
		L.remove(L[i])
		return U

	def producepath(self,G,u,v):
		try:
			l,p = nx.bidirectional_dijkstra(G,u,v)
			return l,p
		except:
			return False,False

	def add_keys_to_nodes(self,G,p):
		T = []
		for n in p:
			T.append((n,G.node[n]['key']))
		return T

	#The attack proceeds until all the discovered nodes fail.
	#G: My understanding of the graph
	#U: To invade next.
	def basic(self,G=nx.DiGraph(),U=0):
		#Needed if calling basic directly.
		#G.add_node(0)
		#G.node[0]['key'] = '0'
		L = [] #Next level received from the victim's network
		D = [] #Trajectory
		wrong = 0 #Wrong path instances / all trails
		trials = 0 #All trials
		failed = True

		self.announcestart()

		for i in range(0,4000):
			#Increase trials
			trials = trials + 1
			#Who is available for invading next?
			l,p = nx.bidirectional_dijkstra(G,0,U)

			#Add keys to nodes
			T = self.add_keys_to_nodes(G,p)

			#print 'building path: ', T, p
			#print 'Graph: ', G.edges()

			#Record discovered nodes received from server.
			New = self.talktocloud(T)
			#print 'chosen: ', U , ' to discover: ', New

			if len(New) == 0:
				#Path was wrong, remove it.
				#No need for this right now. I don't know why I added it?
				#self.removepathfromgraph(G,p)
				wrong=wrong+1
				pass
			else:
				#Update the view of the graph
				#by including more edges.
				self.addnexttograph(G,U,New)

				#Take the list of nodes available for disocvery. No need for the keys in this list, so filter them out.
				L = L + [n for n,k in New]

			#If I have the last node in the list, I'm done! But, if the linkt to target is changing, this isn't enough to claim victory.
			if targetnode in L:
				self.terminationreport(D)
				failed = False
				break

			#If I have no more nodes to invade, I failed!
			elif len(L) == 0:
				self.terminationreport(D,False)
				break

			#Pick one of the available nodes to invade next
			U = self.pickanodetoinvade(L,D)

			#Launch an attack
			self.compromise(U)
		return (D,failed,float(wrong)/float(trials))

	#The attack proceeds until all the discovered nodes fail.
	#When a failure occurs, the attacker restarts from the top.
	def restart(self):
		G=nx.DiGraph()
		D = [] #Trajectory
		failed = True
		for i in range(0,200):
			U = 0
			T,failed = self.basic(G,U)
			D = D + T
			if not failed:
				break

		print 'Final trajectory: ', D
		return (D,failed)

	#The attack proceeds until all the discovered nodes fail.
	#When a failure occurs, the attacker either backtracks to one
	#of the nodes in the trajectory or restarts.
	def backtrack(self):
		G=nx.DiGraph()
		G.add_node(0)
		G.node[0]['key'] = '0'
		D = [0] #Trajectory
		wrong = 0  #Wrong ratios aggregate
		failed = True
		U = 0
		for i in range(0,4000):
			T,failed,wrongratio = self.basic(G,U)
			D = D + T
			wrong = wrong + wrongratio

			if not failed:
				break
			else:
				#Toss a coin and either pick a node from
				#D or restart.
				#coin = random.randint(0,1)
				coin = 0
				if coin == 0:
					U = 0
					G = nx.DiGraph()
					G.add_node(0)
					G.node[0]['key'] = '0'
					#print 'Decided to restart'
				else:
					#Pick a node from D
					i = random.randint(0,len(D)-1)
					U = D[i]
					#print 'Decided to backtrack to ', U

		return (D,failed,wrong)


	def statistics(self,data,successes,fails,duration=None):
		location = self.dataloc
		f = open(location+"/"+str(self.delay)+".m", 'a+')
		f.write("%Results:\n")
		f.write('mu = '+str(np.average(data))+";\n")
		f.write('sd = '+str(np.std(data))+";\n")
		f.write('med = '+str(np.median(data))+";\n")
		f.write('max = '+str(np.nanmax(data))+';\n')
		f.write('min = '+str(np.nanmin(data))+';\n')
		f.write('n = '+str(len(data))+";\n")
		f.write('failed = '+str(fails)+";\n")
		f.write('delay = '+str(self.delay)+";\n")
		f.write('duration = '+str(duration)+";\n")
		f.write('row'+str(self.delay).replace(".","")+"= [mu med sd min max];\n")
		f.close()

	def rawdataout(self,data):
		location = self.dataloc
		f = open(location+"/"+str(self.delay)+".m", 'a+')
		f.write("%Raw:\n")
		f.write("raw = [ ")
		for d in data:
			f.write(str(len(d))+" ")
		f.write("];\n")
		f.close()

	def rawdataoutdirect(self,data):
		location = self.dataloc
		f = open(location+"/"+str(self.delay)+".m", 'a+')
		f.write("%Raw:\n")
		f.write("raw = [ ")
		for d in data:
			f.write(str(d)+" ")
		f.write("];\n")
		f.close()


	#Run the basic attack multiple times
	def multiple_basic(self):
		Dlist = []
		tsizes = []
		s,f = (0,0)
		for i in range(0,20):
			D,failed = self.basic()
			Dlist.append(D)
			tsizes.append(len(D))
			if failed:
				f+= 1
			else:
				s+= 1
		self.statistics(tsizes,s,f)

	#Run the restart attack multiple times
	def multiple_restart(self):
		Dlist = []
		tsizes = []
		s,f = (0,0)

		for i in range(0,20):
			D,failed = self.restart()
			Dlist.append(D)
			tsizes.append(len(D))
			if failed:
				f+= 1
			else:
				s+= 1
		self.statistics(tsizes,s,f)

	#Run the backtrack attack multiple times
	def multiple_backtrack(self):
		Dlist = []
		Wlist = []
		tsizes = []
		s,f = (0,0)
		time = datetime.datetime.now()
		end = None
		avg = datetime.timedelta(0,0,0)
		for i in range(0,1000):
			D,failed,W = self.backtrack()
			if len(D) < 10:
				print 'Trajectory: ', D
			#Track duration
			end = datetime.datetime.now()
			avg = avg + end-time
			time = end
			#End track duration
			Dlist.append(D)
			Wlist.append(W)
			tsizes.append(len(D))
			if failed:
				f+= 1
			else:
				s+= 1
			print i, ' backtrack done: ', len(D), ' ', datetime.datetime.now()

		self.statistics(tsizes,s,f,avg)
		self.rawdataout(Dlist)
		self.rawdataoutdirect(Wlist)




def multiple_attacks(port,dataloc):
	print 'Multiple attacks...'
	compromise_delay = 0.01
	pool = []
	for i in range(0,8):
		at = Attack(port, compromise_delay, dataloc)
		thread = Thread(target = at.multiple_backtrack, args = ())
		thread.start()
		print thread
		pool.append(thread)
		compromise_delay = compromise_delay * 2

	for t in pool:
		t.join()




def main():
	if len(sys.argv) == 2:
		port = int(sys.argv[1])
	elif len(sys.argv)>2:
		port = int(sys.argv[1])
		compromise_delay = float(sys.argv[2])
		if len(sys.argv) > 3:
			dataloc = sys.argv[3]
	else:
		port = 9999
		compromise_delay = 1

	if compromise_delay > 0:
		at = Attack(port, compromise_delay,dataloc)
		at.multiple_backtrack()
	else:
		multiple_attacks(port,dataloc)

if __name__ == "__main__":
    main()
