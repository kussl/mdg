from host import Host

class Reachability:
    #All hosts in the network can reach each others by default.
    #This will create a set of hosts that can reach host.
    def reachablettohost(self, host, network):
        reachable = set() 
        if host.services == []:
            return set()
        for h in network.getHosts():
            if h is host:
                continue
            reachable.add(h)

        #Check if the machine is connected to another network
        if host.connectedtonet:
            for net in host.connectedtonet:
                for h in net.getHosts():
                    reachable.add(h)

        return self.checkfirewall(host,reachable)

    #This will filter out reachable hosts based on firewall settings.
    def checkfirewall(self,host, reachablehosts):
        assert isinstance(host, Host)
        if host.tcpconfig.allowTCPIn is False:
            return set()

        blacklist = set()
        whitelist = set()

        #Check blocked hosts
        for h in host.tcpconfig.blockedHosts:
            if h in reachablehosts:
                #print 'blocked host (host): '+h.name + " for "+host.name
                blacklist.add(h)

        #Check for blocked OS
        for h in reachablehosts:
            if h.os == next((os for os in host.tcpconfig.blockedOS),None):
                #print 'Blocked host (os): '+h.name

                blacklist.add(h)

        #Check for specific IPs to block
        for h in reachablehosts:
            if h.ip == next((ip for ip in host.tcpconfig.blockedIPs),None):
                #print 'Blocked host (ip): '+h.name
                blacklist.add(h)

        #Check for allowed IPs to whitelist
        for h in reachablehosts:
            if h.ip in host.tcpconfig.allowedIPs or h.pip in host.tcpconfig.allowedIPs:
                #print host.name+ ' allowed ip: '+h.ip
                whitelist.add(h)
            else:
                pass #print 'not allowed ip: '+h.name+" "+h.ip

        #Take out those that cannot make TCP out connections
        for h in reachablehosts:
            if h.tcpconfig.allowTCPOut == False:
                blacklist.add(h)

        if len(blacklist) == 0 and len(whitelist)==0:
            return reachablehosts
        if len(whitelist) == 0:
            reach = reachablehosts.difference(blacklist)
        else:
            reach = (reachablehosts.difference(blacklist)).intersection(whitelist)
        return reach
