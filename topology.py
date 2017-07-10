#!/usr/bin/python
#coding=utf-8

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.cli import CLI


class SingleSwitchTopo(Topo):
    def __init__(self, linkopts, n=4, **opts):
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s0')  # add switch s0
        for h in irange(1,n):
            num = h
            host = self.addHost('h%s'%str(num),mac='00:00:00:00:00:0%s'%num)  
            self.addLink(host, switch, **linkopts)  
topos = {'topology':(lambda:SingleSwitchTopo())}

def topoTest():
    print ("Creating network and run simple performance test")
    linkopts = dict(bw=20, delay='5ms',lose=0, max_queue_size=1000, use_htb='true') 
    topo = SingleSwitchTopo(linkopts)#create topo
    net = Mininet(topo=topo, controller= lambda name:RemoteController(name,ip='0.0.0.0'),link=TCLink) 
    #net = Mininet(topo=topo,link=TCLink) # creating network using local controller
    net.start()    #starting the network
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    CLI(net)
    print "Testing network connectivity"
    #net.pingAll()    #ping each hosts
    #net.stop()       # stop the network

if __name__ == '__main__':
    setLogLevel('info')  # set Mininet's log level, info 
    topoTest()
