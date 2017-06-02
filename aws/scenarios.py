
from generator import Generator
from network import *
from firewall import Firewall
from graph import GraphConstructor
from aws import AWSModel

class Scenarios:
    def printhosts(hosts):
        for h in hosts:
            print h.ip, ' ', h.os

    def defaultnetwork(self):
        no_hosts = 8

        g = Generator()
        network = g.generate_network(no_hosts,1)
        network.subnets.append(Subnet(g.generate_hosts(no_hosts,no_hosts,"Windows")))

        #Attacker network
        attacker = g.generate_attacker_network(2)

        #Isolated network
        hosts = g.generate_hosts_custom(int(no_hosts/3),os="Mac", start=no_hosts*3+1, startip='196.0.5.')
        isolated = g.generate_single_subnet_network(hosts)

        print 'All machines: '+str(len(network.getHosts())+len(isolated.getHosts()))
        print 'Attackers: '+str(len(attacker.getHosts()))

        attacker.name = "Attacker"
        isolated.name = "Isolated"

        return [network, attacker, isolated]

    def test_scenario_1(self):
        networks = self.defaultnetwork()
        network = networks[0]
        attacker = networks[1]
        isolated = networks[2]

        hosts = network.getHosts()
        fw = Firewall()
        extra_services = fw.add_http_service_rand(hosts, 0.5)
        disabled_services = fw.disable_services_rand(hosts, 0.5)
        disabled_tcpout = fw.disable_tcpout_rand(hosts, 0.5)
        whitelisted = fw.whitelist_rand(hosts, 0.5)
        connected_attacker = fw.connect_othernetwork_rand(hosts, 0.5, attacker)
        blockedos = fw.block_machines_with_os(hosts, 0.1)

        #Mac machines are in isolated network. Only one device
        #will be connected to a machine that is accessible internally
        #but not from the attacker network
        machine = None
        for h in hosts:
            if h in whitelisted and h not in disabled_tcpout and h not in connected_attacker:
                machine = h
        isolated_hosts = isolated.getHosts()

        print 'Picking machine '+machine.name + ' to connect to '+ isolated_hosts[0].name

        network.compute_reachability()
        hosts[int(machine.name)].reachablefrom.add(isolated_hosts[0])

        isolated.compute_reachability()
        isolated_hosts[0].reachablefrom.add(machine)

        gc = GraphConstructor()
        G = gc.generate_multiple_networks(networks)
        gc.visualize_graph(G)

        [longest_path,nopath,foundpath] = gc.find_all_paths_from_network(G, hosts+isolated_hosts, attacker)
        print 'Reachable paths: '+str(foundpath)
        print 'Unreachable paths: '+str(nopath)
        print 'Longest path: ', longest_path

    def longest_attack_path(self, G, hosts, attacker):
        gc = GraphConstructor()
        [longest_path,nopath,foundpath] = gc.find_all_paths_from_network(G, hosts, attacker)
        print 'Reachable paths: '+str(foundpath)
        print 'Unreachable paths: '+str(nopath)
        print 'Longest path: ', longest_path

    def aws_scenario_1(self):
        aws = AWSModel()
        g = Generator()
        fw = Firewall()
        gc = GraphConstructor()
        networks = aws.aws_network_model()
        # attacker = g.generate_attacker_network(1)
        # attacker.name = "Internet Attacker"
        # fw.connect_othernetwork_rand(networks[0].getHosts(),1.0,attacker)
        # for net in networks:
        #      net.compute_reachability()
        #G = gc.generate_multiple_networks(networks+[attacker])
        G = gc.generate_multiple_networks(networks)
        gc.draw_with_dot(G)
        # gc.visualize_graph(G)
        # self.longest_attack_path(G, aws.all_hosts_in_networks(networks), attacker)

    def aws_scenario_2(self, nosynthetichosts):
        aws = AWSModel()
        g = Generator()
        fw = Firewall()
        gc = GraphConstructor()
        networks = aws.aws_network_model_with_synthetic(nosynthetichosts)
        attacker = g.generate_attacker_network(1)
        attacker.name = "Internet Attacker"
        fw.connect_othernetwork_rand(networks[0].getHosts(),1.0,attacker)
        for net in networks:
            net.compute_reachability()
        G = gc.generate_multiple_networks(networks+[attacker])
        gc.visualize_graph(G)
        self.longest_attack_path(G, aws.all_hosts_in_networks(networks), attacker)
