# Copyright (C) 2016 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

#スイッチングハブと同じ挙動を促すSDN Controller
class ExampleSwitch13(app_manager.RyuApp): #ryu.app_manaegr.RyuAppを継承してRyuアプリケーションを作成する。
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION] #バージョンはOpenFlow 1.3を指定

    def __init__(self, *args, **kwargs):
        super(ExampleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {} # macアドレスを保持するテーブル
    # Ryuでは、受け取りたいOpenFlowメッセージごとにイベントハンドラを実装する。
    # set_ev_clsでは、引数に受け取るメッセージに対応したイベントクラスとOpenFlowスイッチのステートを指定する。
    # 第一引数：イベントクラス名 "ofp_event.EventOFP<OpenFlowメッセージ名>"
    # 第二引数: ステート(ryu.controller.handlerを参照)
    #
    # コントローラが機能要求をスイッチに送信すると、スイッチはスイッチ自身の基本的な機能要求をFeatures reply messageとして返す。
    # この動作は一般的にチャネル確立時に行われるため、このタイミングでTable-missフローエントリー(優先度が0で全てのフローにマッチするエントリ)の定義・追加をする。
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER) # イベント：Features reply message(チャネル確立時に実行される)
    # ev.msgには、イベントに対応するOpenFlowメッセージクラスのインスタンスが格納される。
    # 基本的にこれをいじいじする。
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath # OpenFlowスイッチとの実際の通信処理や受信メッセージに対応したイベントの発行などをする。重要。
        ofproto = datapath.ofproto # ofprotoモジュール：OpenFlowプロトコルを表現する？？要チェック
        parser = datapath.ofproto_parser# ofproto_parserモジュール👆と同じで要チェック

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)# table-miss フローの追加

    # フローを追加するメソッド
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        # 第一引数： インストラクション (マッチに該当するパケットを受信した時の動作)
        # 第二引数： アクション(パケット転送等)
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)] #OFIPIT_APPLY_ACTIONSは指定したアクションを即時実行する。
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst) #OFPFlowModeクラスのインスタンスを生成。
        datapath.send_msg(mod) # OpenFlowスイッチにメッセージを送信。

    # Packet-Inハンドラ
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # get Datapath ID to identify OpenFlow switches.
        dpid = datapath.id #どのOpenFlowスイッチからのPacket-Inかを識別できる。
        self.mac_to_port.setdefault(dpid, {}) #辞書のkeyはこのDatapthIDにしているらしい

        # analyse the received packets using the packet library.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        # get the received port number from packet_in message.
        in_port = msg.match['in_port'] #matchメソッドからスイッチの受信ポートを取得。

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port # {DatapathID:{MAC:Port}}

        # if the destination mac address is already learned,
        # decide which port to output the packet, otherwise FLOOD.
        if dst in self.mac_to_port[dpid]: #学習中のテーブルに宛先が既に入っていればそのポートに、そうでなければ全体に。。。。
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD #フラッディング：全ポートに転送してくれってやつ。

        # construct action list.
        actions = [parser.OFPActionOutput(out_port)]

        # フローテーブルに追加。
        if out_port != ofproto.OFPP_FLOOD: 
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst) #ここでどんなフローにマッチするかを指定している。
            self.add_flow(datapath, 1, match, actions)

        # construct packet_out message and send it.
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
        datapath.send_msg(out)
