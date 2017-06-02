from random import randint

from host import Service


class Firewall:
    def randomhosts(self,hosts, limit, excepthost=None):
        selectedhosts = []
        for i in range(0, limit):
            rand = randint(0,len(hosts)-1)
            if hosts[rand] == excepthost:
                i=i-1
                continue
            selectedhosts.append(hosts[rand])
        return selectedhosts

    def disable_services_rand(self, hosts, percentage):
        limit = int(len(hosts)*percentage)
        machines = []
        print 'Disabling for: '+str(limit)
        for i in range(0, limit):
            rand = randint(0,len(hosts)-1)
            hosts[rand].services = []
            machines.append(hosts[rand])
        return machines

    def disable_tcpout_rand(self, hosts, percentage):
        limit = int(len(hosts)*percentage)
        print 'Disabling tcpout for: '+str(limit)
        machines = []
        for i in range(0, limit):
            rand = randint(0,len(hosts)-1)
            hosts[rand].tcpconfig.allowTCPOut = False
            machines.append(hosts[rand])
        return machines

    def whitelist_rand(self, hosts, percentage):
        limit = int(len(hosts)*percentage)
        print 'Whitelisting for: '+str(limit)
        machines = []
        for i in range(0, limit):
            rand = randint(0,len(hosts)-1)
            whitelist = self.randomhosts(hosts, int(limit*.5), hosts[rand])
            for h in whitelist:
                hosts[rand].tcpconfig.allowedIPs.append(h.ip)
            machines.append(hosts[rand])
        return machines

    def connect_othernetwork_rand(self, hosts, percentage, othernetwork):
        limit = int(len(hosts)*percentage)
        print 'Connection to '+othernetwork.name+' for '+str(limit)+' machines.'
        machines = []
        for i in range(0, limit):
            rand = randint(0,len(hosts)-1)
            hosts[rand].connectedtonet.append(othernetwork)
            machines.append(hosts[rand])
        return machines

    def add_http_service_rand(self, hosts, percentage):
        limit = int(len(hosts)*percentage)
        print 'Extra services for '+str(limit)+' machines.'
        machines = []
        for i in range(0, limit):
            rand = randint(0, len(hosts)-1)
            if rand not in machines:
                hosts[rand].services.append(Service('http',80))
                machines.append(hosts[rand])
        return machines

    def block_machines_with_os(self, hosts, percentage, os="Windows"):
        limit = int(len(hosts)*percentage)
        print 'Blocking '+os+' for '+str(limit)+' machines.'
        machines = []
        for i in range(0, limit):
            rand = randint(0, len(hosts)-1)
            if rand not in machines:
                hosts[rand].tcpconfig.blockedOS.append(os)
                machines.append(hosts[rand])
        return machines