
class TcpHostConfig:
    def __init__(self):
        self.allowTCPIn = True
        self.allowTCPOut = True
        self.blockedIPs = []
        self.blockedHosts = []
        self.allowedIPs = []
        self.blockedOS = []

class Service:
    def __init__(self,name="ssh", port=22):
        self.name = name
        self.port = port

class Host:
    def __init__(self, ip=None,name=None,os="Linux",services=None,tcpconfig=None,reachablefrom=None,pip=None):
        self.ip = ip
        self.pip = pip #Public IP
        self.name = name
        self.os = os
        self.tcpconfig = tcpconfig
        self.services = services
        self.reachablefrom = reachablefrom 
        self.connectedtonet = []
        self.network = None
