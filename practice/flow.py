from durable.lang import *

acesslines = []
with ruleset('flow'):

    # アクセス回線の追加
    @when_all(m.subject=='access_line')
    def assert_access_line(c):
        c.assert_fact({
            'subject': c.m.subject,
            'access_line': c.m.access_line,
            'identifier': c.m.identifier,
            'provider': c.m.provider,
            'carrier': c.m.carrier,
            'communication_method': c.m.communication_method,
            'encryption_method': c.m.encryption_method,
            'max_bandwidth': c.m.max_bandwidth,
            'cost': c.m.cost,
            'timeout': c.m.timeout,
            'vorticity_max_bandwitdh': c.m.vorticity_max_bandwitdh,
            'average_utilization': c.m.average_utilization,
            'ip': c.m.ip,
            'mac': c.m.mac })
        print('''assert Fact
        subject:{0}
        access_line:{1},
        identifier:{2}, 
        provider:{3}, 
        carrier:{4}, 
        communication_method:{5},
        encryption_method:{6},
        max_bandwidth:{7}, 
        cost:{8}, 
        timeout:{9}, 
        vorticity_max_bandwitdh:{10},
        average_utilization:{11},
        ip:{12},
        mac:{13}
         '''.format(c.m.subject, c.m.subject, c.m.access_line, c.m.identifier, c.m.provider, c.m.carrier, c.m.communication_method, 
         c.m.encryption_method, c.m.max_bandwidth, c.m.cost, c.m.timeout, c.m.vorticity_max_bandwitdh, c.m.average_utilization, c.m.ip, c.m.mac))

    # Docter's IP: 192.168.13.1
    @when_all((m.subject=='flow_info') & (m.src_ip=='192.168.13.1') & (m.dst_port==25))
    def health_care(c):
        c.assert_fact({'subject':'app_request', 'app_name': 'health_care', 'utilization_rate': None , 'delay': 120, 'packet_loss': 35, 'jitter': None, 'bandwidth': None, 'cost': None ,'security_score': 3})
        
        print('''assert Fact
        subject:{0},
        app_name: {1},
        utilization_rate:{2},
        delay:{3},
        packet_loss:{4},
        jitter:{5},
        bandwidth:{6},
        cost:{7},
        security_score:{8}
        '''.format(c.m.subject, c.m.app_name, c.m.utilization_rate, c.m.delay, c.m.packet_loss, c.m.jitter, c.m.bandwidth, c.m.cost, c.m.security_score))

    @when_all((m.subject=='flow_info') & (m.dst_port==25))
    def email(c):
        # アプリケーション要求： 遅延が20[ms]以下、パケットロスが30%以下、セキュリティが3以上
        c.assert_fact({'subject':'app_request', 'app_name': 'health_care', 'utilization_rate': None , 'delay': 20, 'packet_loss': 30, 'jitter': None, 'bandwidth': None, 'cost': None ,'security_score': 3})

        print('''assert Fact
        subject:{0},
        app_name: {1},
        utilization_rate:{2},
        delay:{3},
        packet_loss:{4},
        jitter:{5},
        bandwidth:{6},
        cost:{7},
        security_score:{8}
        '''.format(c.m.subject, c.m.app_name, c.m.utilization_rate, c.m.delay, c.m.packet_loss, c.m.jitter, c.m.bandwidth, c.m.cost, c.m.security_score))

    @when_all((m.subject=='flow_info') & (m.dst_port==5060))
    def voip(c):
        c.assert_facts({'subject':'app_request', 'app_name': 'health_care', 'utilization_rate': None , 'delay': 20, 'packet_loss': 30, 'jitter': None, 'bandwidth': None, 'cost': None ,'security_score': 3})

        print('''assert Fact
        subject:{0},
        app_name: {1},
        utilization_rate:{2},
        delay:{3},
        packet_loss:{4},
        jitter:{5},
        bandwidth:{6},
        cost:{7},
        security_score:{8}
        '''.format(c.m.subject, c.m.app_name, c.m.utilization_rate, c.m.delay, c.m.packet_loss, c.m.jitter, c.m.bandwidth, c.m.cost, c.m.security_score))

    # will be chained after asserting application requests
    # check if AL1 can be used
    @when_all((m.subject == 'app_request') & (m.delay > 100) & (m.packet_loss > 30) & (m.security_score < 4))
    def acessline_check_1(c):
        print("This flow can't use line1")
        lines['line1'] = False
    
    @when_all((m.subject == 'app_request') & (m.delay > 100) & (m.packet_loss > 30) & (m.security_score < 10))
    def acessline_check_2(c): 
        print("This flow can't use line2")
        lines['line2'] = False
    
    @when_all((m.subject == 'app_request') & (m.utilizatino_rate > 90) & (m.packet_loss > 30))
    def acessline_check_3(c): 
        print("This flow can't use line3")
        lines['line3'] = False

    @when_all(+m.subject)
    def output(c):
        pass

lines = {'line1': True, 'line2': True, 'line3': True}
#回線情報のファクトを追加
post('flow', {'subject': 'access_line', 'access_line': 'Wi-Fi', 'identifier': 'wifi001', 'provider': 'suganuma_lab', 'carrier': 'TAINS',  'communication_method': 'IEEE802.11a', 'encryption_method': 'WEP', 'max_bandwidth': 54000, 'cost': 0, 'timeout': 1000, 'vorticity_max_bandwidth': 20000, 'average_utilization': 20, 'ip':'192.168.100.2', 'mac': '00:23:18:A1:6b:57'})

post('flow', {'subject': 'access_line', 'access_line': 'UQ-WiMAX', 'identifier': 'wimax002', 'provider': 'UQ', 'carrier': 'KDDI',  'communication_method': 'IEEE802.16', 'encryption_method': 'AES', 'max_bandwidth': 50000, 'cost': 2500, 'timeout': 100000, 'vorticity_max_bandwidth': 30000, 'average_utilization': 50, 'ip':'192.168.100.3', 'mac': '00:23:18:A1:6b:51'})

# フロー情報のファクトを追加
post('flow', {'subject': 'flow_info', 'src_ip': '192.168.13.1', 'dst_ip': '74.125.235.84', 'src_port': 65534, 'dst_port': 25, 'layer3': 'TCP', 'layer4': 'SMTP'})

print(lines)