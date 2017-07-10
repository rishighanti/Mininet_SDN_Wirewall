#!/usr/bin/python

from pox.core  import core

from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr
from pox.lib.recoco import Timer
from pox.openflow.of_json import *

log = core.getLogger(); # use core's log function

#msg = of.ofp_flow_mod()
#print msg
#test = pox.core.openflow._connections.values()



def _timer_func():
    # connection and send message to switch
    for connection in core.openflow._connections.values():
        connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    log.debug("Sent %i flow stats requests",len(core.openflow._connections))
#_timer_func()

def _handle_flowstats_received(event):
    stats = flow_stats_to_list(event.stats)  #get event stats
    log.debug("Flow stats received from %s:%s",dpidToStr(event.connection.dpid),stats)
    global flow_bytes_past # last recording flow bytes
    global max_bytes  # max value
    global max_addr # max value' address

    flow_bytes_now = 0
    flow_bytes = 0
    flow_bandwidth = 0   # bandwidth

    for f in event.stats:
        if f.match.dl_dst == EthAddr("00:00:00:00:00:01"): 
            flow_bytes_now += f.byte_count;
            if f.byte_count > max_bytes:  
                max_bytes = f.byte_count
                max_addr = f.match.dl_src   
    flow_bytes = flow_bytes_now - flow_bytes_past  
    #flow_bandwidth = (flow_bytes*8.0/5.0)/1000000.0
    flow_bandwidth = (flow_bytes*8.0)/1000000.0  
    flow_bytes_past = flow_bytes_now
    #if there is data to h1
    if flow_bandwidth >= 0:
        log.info("Traffic to h1 is %s bytes ",flow_bytes)
        log.info("Traffic to h1 is %s  bandwidth ",flow_bandwidth)
        msg = of.ofp_flow_mod() # create message object
        msg.match = of.ofp_match()
        threshold = 16  # set threshold 16 here
        if flow_bandwidth > threshold: 
            msg.match.dl_src = max_addr; 
            msg.match.dl_dst = EthAddr("00:00:00:00:00:01")
            event.connection.send(msg)
            #if src address is host 2
            if max_addr == EthAddr("00:00:00:00:00:02"):
                log.info("Overload: Packets from h2 are dropped")
            #if src address is host 3
            if max_addr == EthAddr("00:00:00:00:00:03"):
                log.info("Overload: Packets from h3 are dropped")
            #if src address is host 4
            if max_addr == EthAddr("00:00:00:00:00:04"):
                log.info("Overload: Packets from h4 are dropped")
	else:
	    msg.match.dl_src = max_addr;  #set msg match's address
            msg.match.dl_dst = EthAddr("00:00:00:00:00:01")
            event.connection.send(msg)
            #if src address is host 2
            if max_addr == EthAddr("00:00:00:00:00:02"):
                log.info("Packets from h2 are forwarded")
            #if src address is host 3
            if max_addr == EthAddr("00:00:00:00:00:03"):
                log.info("Packets from h3 are forwarded")
            #if src address is host 4
            if max_addr == EthAddr("00:00:00:00:00:04"):
                log.info("Packets from h4 are forwarded")
    else:
        #if not exceed the threshold
        log.info("sending packets successfully")
def launch():
    # initialing
    global flow_bytes_past
    flow_bytes_past = 0  # set to 0
    global max_bytes
    max_bytes = 0 # set to 0
    global max_addr
    max_addr = EthAddr("00:00:00:00:00:00")  
    # band listener
    core.openflow.addListenerByName("FlowStatsReceived",_handle_flowstats_received)
    # set Timer to five seconds, and call function _timer_func, make recurring ture
    Timer(1,_timer_func,recurring = True)





