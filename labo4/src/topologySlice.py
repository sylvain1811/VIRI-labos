from pox.core import core
from collections import defaultdict

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os

log = core.getLogger()


class TopologySlice(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Enabling Slicing Module")

    def set_output(self, out_port, in_port, event):
        fm = of.ofp_flow_mod()
        fm.match.in_port = in_port
        fm.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(fm)

    """This event will be raised each time a switch will connect to the controller"""

    def _handle_ConnectionUp(self, event):

        # Use dpid to differentiate between switches (datapath-id)
        # Each switch has its own flow table. As we'll see in this
        # example we need to write different rules in different tables.
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)

        """ Add your logic here """

        if "1" in dpid:
            self.set_output(1, 3, event)
            self.set_output(3, 1, event)
            self.set_output(4, 2, event)
            self.set_output(2, 4, event)
        if "2" in dpid:
            self.set_output(1, 2, event)
            self.set_output(2, 1, event)
        if "3" in dpid:
            self.set_output(1, 2, event)
            self.set_output(2, 1, event)
        if "4" in dpid:
            self.set_output(1, 3, event)
            self.set_output(3, 1, event)
            self.set_output(4, 2, event)
            self.set_output(2, 4, event)


def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    """
    Starting the Topology Slicing module
    """
    core.registerNew(TopologySlice)
