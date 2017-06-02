from network import Network, Subnet
from host import Host, Service, TcpHostConfig

class Generator:
    def __init__(self):
        pass
    def generate_hosts(self, no_hosts, counter_start=0, os="Linux"):
        hosts = []
        for ip_counter in range(counter_start,no_hosts+counter_start):
            host = Host('192.0.1.'+str(ip_counter), str(ip_counter), os=os, services=[Service('ssh',22)])
            host.tcpconfig = TcpHostConfig()
            hosts.append(host)
        return hosts

    def generate_hosts_custom(self, no_hosts, os="Linux", start=0, startip='192.0.0.', services=[Service('ssh',22)]):
        hosts = []
        for i in range(start, no_hosts+start):
            host = Host(startip+str(i),str(i), os=os, services=services)
            host.tcpconfig = TcpHostConfig()
            hosts.append(host)
        return hosts

    def generate_single_subnet_network(self, hosts):
        return Network([Subnet(hosts)])


    def generate_network(self, no_hosts, no_subnets, os="Linux"):
        subnets = []
        for i in range(0, no_subnets):
            subnet = Subnet(self.generate_hosts(no_hosts, i*no_hosts, os))
            subnets.append(subnet)
        return Network(subnets)

    def generate_attacker_network(self, no_hosts):
        if no_hosts < 0:
            return None
        hosts = []
        for i in range(1, no_hosts+1):
            host = Host('12.0.1.'+str(i), str(i+300), os="Linux", services=[Service('ssh',22)])
            host.tcpconfig = TcpHostConfig()
            hosts.append(host)
        subnet = Subnet(hosts)
        return Network([subnet])

