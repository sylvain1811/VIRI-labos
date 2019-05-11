#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange,dumpNodeConnections
from mininet.link import TCLink
from mininet.log import setLogLevel


class CustomTopology(Topo):
    """
    linkoptions1: core options
    linkoptions2: aggregation options
    linkoptions3: edge options
    fanout: number of child switch per parent switch
    """
    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **otheroptions):
        # Initialize topology and default options
        Topo.__init__(self, **otheroptions)
        
        # INCOMPLETE --- Add your logic here ...
    
    
        # END
    
    
def simpleTest():
    "Test"
    linkopts1 = dict(bw=1000, delay='1ms')
    linkopts2 = dict(bw=100, delay='10ms')
    linkopts3 = dict(bw=10, delay='20ms')
    fanout = 2
    
    topo = CustomTopology(linkopts1, linkopts2, linkopts3, fanout)
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    
    print "Testing bandwidth between h1 and h8"
    h1, h8 = net.get('h1', 'h8')
    net.iperf((h1, h8))
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
