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


class VideoSlice(EventMixin):
    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)

        # Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
        self.adjacency = defaultdict(lambda: defaultdict(lambda: None))

        """
        The structure of self.portmap is a four-tuple key and a string value.
        The type is:
        (dpid string, src MAC addr, dst MAC addr, port (int)) -> dpid of next switch
        """

        self.portmap = {
            # VIDEO (tcp port 80)
            # h1 -> h3
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:03"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:03"),
                80,
            ): "00-00-00-00-00-04",
            # h3 -> h1
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:01"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:01"),
                80,
            ): "00-00-00-00-00-01",
            # h2 -> h3
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:03"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:03"),
                80,
            ): "00-00-00-00-00-04",
            # h3 -> h2
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:02"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:02"),
                80,
            ): "00-00-00-00-00-01",
            # h1 -> h4
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:04"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:04"),
                80,
            ): "00-00-00-00-00-04",
            # h4 -> h1
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:01"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:01"),
                80,
            ): "00-00-00-00-00-01",
            # h2 -> h4
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:04"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:04"),
                80,
            ): "00-00-00-00-00-04",
            # h4 -> h2
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:02"),
                80,
            ): "00-00-00-00-00-03",
            (
                "00-00-00-00-00-03",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:02"),
                80,
            ): "00-00-00-00-00-01",
            # NON-VIDEO (tcp port not 80)
            # h1 -> h3
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:03"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:03"),
                None,
            ): "00-00-00-00-00-04",
            # h3 -> h1
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:01"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:01"),
                None,
            ): "00-00-00-00-00-01",
            # h2 -> h3
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:03"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:03"),
                None,
            ): "00-00-00-00-00-04",
            # h3 -> h2
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:02"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:03"),
                EthAddr("00:00:00:00:00:02"),
                None,
            ): "00-00-00-00-00-01",
            # h1 -> h4
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:04"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:01"),
                EthAddr("00:00:00:00:00:04"),
                None,
            ): "00-00-00-00-00-04",
            # h4 -> h1
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:01"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:01"),
                None,
            ): "00-00-00-00-00-01",
            # h2 -> h4
            (
                "00-00-00-00-00-01",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:04"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:02"),
                EthAddr("00:00:00:00:00:04"),
                None,
            ): "00-00-00-00-00-04",
            # h4 -> h2
            (
                "00-00-00-00-00-04",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:02"),
                None,
            ): "00-00-00-00-00-02",
            (
                "00-00-00-00-00-02",
                EthAddr("00:00:00:00:00:04"),
                EthAddr("00:00:00:00:00:02"),
                None,
            ): "00-00-00-00-00-01",
        }
        self.porttohost = {
            ("00-00-00-00-00-04", EthAddr("00:00:00:00:00:03")): 3,
            ("00-00-00-00-00-04", EthAddr("00:00:00:00:00:04")): 4,
            ("00-00-00-00-00-01", EthAddr("00:00:00:00:00:01")): 3,
            ("00-00-00-00-00-01", EthAddr("00:00:00:00:00:02")): 4,
        }

    def _handle_LinkEvent(self, event):
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)

        log.debug("link %s[%d] <-> %s[%d]", sw1, l.port1, sw2, l.port2)

        self.adjacency[sw1][sw2] = l.port1
        self.adjacency[sw2][sw1] = l.port2

    def _handle_PacketIn(self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """
        packet = event.parsed
        tcpp = event.parsed.find("tcp")

        def install_fwdrule(event, packet, outport):
            msg = of.ofp_flow_mod()
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.actions.append(of.ofp_action_output(port=outport))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        def forward(message=None):
            this_dpid = dpid_to_str(event.dpid)

            if packet.dst.is_multicast:
                flood()
                return
            else:
                log.debug(
                    "Got unicast packet for %s at %s (input port %d) on %s",
                    packet.dst,
                    dpid_to_str(event.dpid),
                    event.port,
                    tcpp,
                )

                try:
                    """ Add your logic here"""
                    if tcpp is None:
                        raise AttributeError()

                    log.debug("TCPP is not None : %s", tcpp)
                    key = (this_dpid, packet.src, packet.dst, tcpp.dstport)
                    if tcpp.dstport != 80:
                        key = (this_dpid, packet.src, packet.dst, None)
                    if key in self.portmap:
                        switch_dst = self.portmap[key]
                        log.debug("Outport : %s", self.adjacency[this_dpid][switch_dst])
                        install_fwdrule(
                            event, packet, int(self.adjacency[this_dpid][switch_dst])
                        )
                    else:
                        key = (this_dpid, packet.dst)
                        if key in self.porttohost:
                            outport = self.porttohost[key]
                            install_fwdrule(event, packet, outport)

                except AttributeError:
                    log.debug("packet type has no transport ports, flooding")

                    # flood and install the flow table entry for the flood
                    install_fwdrule(event, packet, of.OFPP_FLOOD)

        # flood, but don't install the rule
        def flood(message=None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        forward()

    def _handle_ConnectionUp(self, event):
        dpid = dpidToStr(event.dpid)
        log.debug("Switch %s has come up.", dpid)


def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    """
    Starting the Video Slicing module
    """
    core.registerNew(VideoSlice)