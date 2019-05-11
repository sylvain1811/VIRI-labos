from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
''' Add your imports here, eg 'csv', ... '''
import csv


log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]  

''' Add your global variables here ... '''
global policies

with open(policyFile, 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    policies = [d for d in reader]


class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):    
        ''' Add your logic here ... '''

        for policy in policies:
            mac_0 = EthAddr(policy['mac_0'])
            mac_1 = EthAddr(policy['mac_1'])

            fm = of.ofp_flow_mod()
            fm.match.dl_src = mac_0
            fm.match.dl_dst = mac_1
            fm.priority = 10
            event.connection.send(fm)

            fm = of.ofp_flow_mod()
            fm.match.dl_src = mac_1
            fm.match.dl_dst = mac_0
            fm.priority = 11
            event.connection.send(fm)

        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)
