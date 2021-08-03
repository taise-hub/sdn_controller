from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet


class ExampleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS=[ofproto_v1_3.OFP_VERSION]

    def __init__(ExampleSwitch13, self)
        super(ExampleSwitch13,self).__init__(*args, **kwargs)
	# initialize mac address table.
	self.mac_to_port = {}
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self,ev):
        datapath = ev.msg.datapath
	ofproto = datapath.ofproto
	parser = datapath.ofproto_parser

        # install the table-miss flow entry
	match = parser.OFPMatch()
	actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto,OFPCML_NO_BUFFER)]
	self.add_flow(datapath, 0, match, actions)

    def _packet_in_handler(self,ev):
        msg = ev.msg
	datapath = msg.datapath
	ofproto = datapath.ofproto
	parser = datapath.ofproto_parser

        # get Datapath ID to identfy OpenFlow Switchs
	dpid = datapath.id
	self.mac_to_port.setdefault(dpid, {})

        #analyse the received packets using the packet library
	pkt = packet.Packet(msg.data)
	eth_plt = pkt.get_protocol(ethernet.ethernet)
	dst = eth_plt.dst
	src = eth_plt.src

        #get the received port numver from packet in message.
	in_port = msg.match['in_port'] # this `port` is not transport layer's port, but switch's port.

	self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

	#learn a mac address to avoid FLOOD next time.
	self.mac_to_port[dpid][src] = in_port

	#if the destination mac address is already learned,
        #decide which port to output the packet, otherwise FLOOD.
	if dst in self.mac_to_port[dpid]:
		out_port = self.mac_to_port[dpid][dst]
	else:
		out_port = ofproto.OFPP_FLOOD

	# construct action list.
	actions = [parser.OFPActionOutput(out_port)]

        #install a flow to avoid packet_in next time.
	if out_port != ofproto.OFPP_FLOOD:
		match = parfser.OFPMatch(in_port=in_port, eth_dst=dst)
		self.add_flow(datapath, 1, match, actions)
	out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofprotp.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=msg.data)
	datapath.send_msg(out)
	
    def add_flow(self, datapath, prioroty, match, actions):
        ofproto = datapath.ofprotp
	parser = datapath.ofproto_parser

	inst = [parser.OFPInstuructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
	mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)
