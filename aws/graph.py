from random import randint

import networkx as nx
import matplotlib.pyplot as plt

class GraphConstructor:
    def generate(self, network, given=None):
        if given is not None:
            G=given
        else:
            G=nx.DiGraph()
        for v in network.getHosts():
            if False == G.has_node(v.name):
                G.add_node(v.name)
            if v.reachablefrom is None:
                continue
            for u in v.reachablefrom:
                if False == G.has_node(u.name):
                    G.add_node(u.name)
                if False == G.has_edge(u.name, v.name):
                    #Add an edge for every available service
                    for i in range(0, len(v.services)):
                        G.add_edge(u.name, v.name, weight=i)
        return G

    def draw_with_dot(self,G,name='connectivity'):
        nx.nx_agraph.write_dot(G,name+".dot")

    def generate_multiple_networks(self, networks):
        G=nx.DiGraph()
        for network in networks:
            G = self.generate(network, G)
        return G

    def visualize_graph_details(self, G):
        edge_labels=dict([((u,v,),d['weight'])
                 for u,v,d in G.edges(data=True)])
        pos = dict()
        i = 0
        for node in G.nodes():
            rand = randint(0,len(G.nodes()))
            rand2 = randint(0,len(G.nodes()))*(int(rand/2))
            pos[node] = (rand,rand2)

        nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
        nx.draw_shell(G,node_color='b',
                      edge_labels=edge_labels,edge_color='g',with_labels=True,arrows=True)
        plt.savefig("graph-d.png")

    def visualize_graph(self, G):
        node_colors = ['blue' if not int(node) > 300 else 'red' for node in G.nodes()]
        pos=nx.fruchterman_reingold_layout(G)
        nx.draw(G,pos, node_color = node_colors,
                node_size=1500,edge_color='g',edge_cmap=plt.cm.Reds,with_labels=True)
        plt.savefig("graph.png")

    def shortest_path(self, G, u, v):
        try:
            path = nx.shortest_path(G,source=u, target=v)
            return path
        except Exception as e:
            return None

    def find_all_paths(self, G, hosts, u):
        print 'Paths from attacker to all nodes: '
        nopath = 0
        longest_length = -1
        longest_path = None
        for h in hosts:
            path = self.shortest_path(G,u, h.name )
            if not path:
                nopath += 1
            else:
                if len(path) > longest_length:
                    longest_length = len(path)
                    longest_path = path
        return [longest_path,nopath]

    def find_all_paths_from_network(self, G, hosts, network):
        nopath = 0
        foundpath = 0
        longest_length = -1
        longest_path = None
        nethosts = network.getHosts()
        for u in nethosts:
            for h in hosts:
                path = self.shortest_path(G,u.name,h.name)
                if not path:
                    nopath += 1
                else:
                    foundpath +=1
                    if len(path) > longest_length:
                        longest_length = len(path)
                        longest_path = path

        return [longest_path,nopath,foundpath]
