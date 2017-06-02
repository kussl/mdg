from reachability import Reachability

class Subnet:
    def subclassinit(self):
        pass
    def __init__(self, hosts=None):
        self.hosts = hosts
        self.name = "Subnet"
        self.subclassinit()

class AWSSubnet(Subnet):
    def subclassinit(self):
        self.cidr_block = None

class Network:
    def __init__(self, subnets=None):
        self.subnets = subnets
        self.name = "Network" #This is just for documentation and testing

    def getHosts(self):
        hosts = []
        for s in self.subnets:
            if s.hosts is not None and len(s.hosts) > 0:
                hosts = hosts + s.hosts
        return hosts

    #This won't return anything. It only has a side-effect.
    #It will calibrate the reachability and update the hosts.
    def compute_reachability(self):
        r = Reachability()
        hosts = self.getHosts()
        for i in range(0, len(hosts)):
            reachable = r.reachablettohost(hosts[i], self)
            hosts[i].reachablefrom = reachable



class VPNetwork(Network):
    def __init__(self):
        self.security_groups = None
