import ipaddress
import boto3
from network import VPNetwork, AWSSubnet
from host import Host, TcpHostConfig, Service
from ipaddress import ip_network

class AWSNetworkInfo:
    def __print_instance(self, instance):
        print(instance.id, instance.private_ip_address, instance.public_ip_address, instance.instance_type)

    def ec2instances(self):
        ec2 = boto3.resource('ec2')
        instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            self.__print_instance(instance)

    def vpcnets(self):
        ec2 = boto3.resource('ec2')
        return ec2.vpcs.all()

    def vpcsubnets(self):
        ec2 = boto3.resource('ec2')
        for vpc in ec2.vpcs.all():
            print 'Instances: '
            for subnet in vpc.subnets.all():
                print (subnet.id, subnet.available_ip_address_count)
                for instance in subnet.instances.all():
                    self.__print_instance(instance)
            print 'Security groups: '
            for sg in vpc.security_groups.all():
                print (sg.group_id, sg.group_name,)
                print 'Permissions: '
                for p in sg.ip_permissions:
                    print p
        return [ec2.vpcs.all()]

    def ec2checkhealth(self):
        ec2 = boto3.resource('ec2')
        base = ec2.instances
        for status in ec2.meta.client.describe_instance_status()['InstanceStatuses']:
            print(status)


class AWSModel:
    def ec2instances(self):
        machines = []
        ec2 = boto3.resource('ec2')
        for instance in ec2.instances.all():
            machines.append(instance)
        return machines

    def ec2_s_groups(self, instance, security_groups):
        groups = []
        for sg in security_groups:
            for isg in instance.security_groups:
                if sg.id == isg['GroupId']:
                   groups.append(sg)
        return groups

    def extract_instance_permissions(self, instance, security_groups):
        groups = self.ec2_s_groups(instance, security_groups)
        permissions = []
        for g in groups:
            for permission in g.ip_permissions:
                permissions.append(permission)
        return permissions

    '''
    Construct a list of allowed IP addresses to connect to the instance.
    This list can be from direct IpRanges.
    '''
    def whitelist_IPs(self,permissions):
        whitelist = []
        for permission in permissions:
            ipranges = permission.get('IpRanges', None)
            if ipranges:
                for range in ipranges:
                    cidrip = range.get('CidrIp')
                    if cidrip:
                        cidripsplit = cidrip.split("/")
                        ip = cidripsplit[0]
                        if ip[0] != '0':
                            whitelist.append(ip)
        return whitelist

    '''
    Construct a list of allowed IP addresses to connect to the instance.
    This list can be from  UserIdGroupPairs which is IP addresses from a particular security group.
    '''
    def whitelist_SecurityGroups(self,permissions):
        whitelist = []
        return whitelist

    '''
    Firewall rules that include instance permissions and a whitelist of IP addresses allowed to connect to the instance.
    '''
    def firewallrules(self,instance, security_groups):
        permissions = self.extract_instance_permissions(instance, security_groups)
        wl1 = self.whitelist_IPs(permissions)
        wl2 = self.whitelist_SecurityGroups(permissions)
        return (permissions, wl1+wl2)

    def all_hosts_in_networks(self, networks):
        hosts = []
        for net in networks:
            hosts = hosts + net.getHosts()
        return hosts

    def find_host_by_ip(self, ip, hosts):
        for h in hosts:
            if h.ip == ip or h.pip == ip:
                return h
        return None

    #If a host's IP is in the allowedIPs list, then
    #we assume the host in allowedIPs is connected to host.
    def connect_host_to_other_networks(self, host, hosts):
        for ip in host.tcpconfig.allowedIPs:
            h = self.find_host_by_ip(ip, hosts)
            if h:
                host.connectedtonet.append(h.network)



    def host_services(self, permissions):
        services = []
        for permission in permissions:
            #Add the open services
            protocol = permission.get('IpProtocol', None)
            port = permission.get('FromPort', None)
            if protocol is None or port is None:
                continue
            service = Service(name=permission['IpProtocol'], port=permission['FromPort'])
            services.append(service)
        return services

    '''
    Only call this from assign_instances_to_subnets to create a new host object. This will also determine host permissions and allowedIPs based on security groups.
    '''
    def create_host(self,instance,security_groups,ip,subnet,network):
        (permissions,whitelist) = self.firewallrules(instance, security_groups)
        hostname = instance.tags[0]['Value']
        host = Host(instance.private_ip_address,
                    hostname,
                    os=instance.platform, services=self.host_services(permissions),
                    pip=instance.public_ip_address)
        host.tcpconfig = TcpHostConfig()
        host.network = network
        host.tcpconfig.allowedIPs = whitelist
        if host.os == None:
            host.os = "Linux"
        if subnet.hosts is None:
            subnet.hosts = []

        print ip,' ',host.name, ' ',host.tcpconfig.allowedIPs
        return host

    '''
    Assign host to subnets
    Determine host permissions
    Create a host object
    Determined allowed IP addresses to connect to the host
    Add host to the list of subnet hosts
    '''
    def assign_instances_to_subnets(self, instances, subnets, security_groups, network):
        for instance in instances:
            ip = ipaddress.ip_address(unicode(instance.private_ip_address))
            for subnet in subnets:
                if ip in list(ipaddress.ip_network(unicode(subnet.cidr_block)).hosts()):
                    host = self.create_host(instance,security_groups,ip,subnet,network)
                    subnet.hosts.append(host)
        return subnets

    '''
    Search host with an IP
    '''
    def whichhost(self, hosts, ip):
        for h in hosts:
            if h.ip == ip:
                return h

    '''
    Determine list of reachable hosts from a host and add them to host's reachablefrom instance.
    '''
    def reachablefrom(self,hosts):
        for host in hosts:
            host.reachablefrom = []
            for rip in host.tcpconfig.allowedIPs:
                u = self.whichhost(hosts,rip)
                host.reachablefrom.append(u)



    def aws_subnet_model(self, vpc):
        subnets = []
        for snet in vpc.subnets.all():
            print 'Subnet: ', snet.cidr_block
            subnet = AWSSubnet()
            subnet.name = snet.id
            subnet.cidr_block = snet.cidr_block
            subnet.hosts = []
            subnets.append(subnet)
        return subnets

    def aws_net_security_groups(self, net):
        groups = []
        ec2 = boto3.resource('ec2')
        for g in ec2.security_groups.all():
            print 'SG: ', g
            groups.append(g)
        return groups

    def add_synthetic_instances(self, network, nohosts):
        if nohosts == 0:
            return []
        hosts = network.getHosts()
        hostips = []
        for h in hosts:
            hostips.append(h.ip)
        subnet = hosts[0].ip.split(".")
        ips = []
        start = 250
        for i in range(start,1,-1):
            if i not in hostips:
                ips.append(i)
        newhosts = []
        for i in range(0, nohosts):
            ip = subnet[0] +"."+ subnet[1]+"." + subnet[2] +"."+ str(ips[i])
            host = Host(ip,str(ips[i]),
                                os="Linux", services=[Service("ssh", "22")],pip=ip)
            host.tcpconfig = TcpHostConfig()
            host.network = network
            newhosts.append(host)
        subnet = AWSSubnet()
        subnet.name = "synthetic"
        subnet.hosts = newhosts
        network.subnets.append(subnet)
        return newhosts


    def aws_network_model(self):
        ec2 = boto3.resource('ec2')
        vpcnets = ec2.vpcs.all()
        networks = []
        for net in vpcnets:
            print 'Network: ', net
            network = VPNetwork()
            network.name = net.id
            network.subnets = self.aws_subnet_model(net)
            network.security_groups = self.aws_net_security_groups(net)
            self.assign_instances_to_subnets(self.ec2instances(), network.subnets, network.security_groups, network)
            networks.append(network)
        hosts = self.all_hosts_in_networks(networks)
        self.reachablefrom(hosts)
        return networks

    def aws_network_model_with_synthetic(self, nosynthetichosts):
        ec2 = boto3.resource('ec2')
        vpcnets = ec2.vpcs.all()
        networks = []
        for net in vpcnets:
            network = VPNetwork()
            network.name = net.id
            network.subnets = self.aws_subnet_model(net)
            network.security_groups = self.aws_net_security_groups(net)
            self.assign_instances_to_subnets(self.ec2instances(), network.subnets, network.security_groups, network)
            self.add_synthetic_instances(network, nosynthetichosts)
            networks.append(network)
            nosynthetichosts = 0

        hosts = self.all_hosts_in_networks(networks)
        #Build relations within networks
        for h in hosts:
            self.connect_host_to_other_networks(h,hosts)

        return networks
