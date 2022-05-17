'''
    # 目前成功实现项目启动前的配置，同时能够启动项目
'''

from asyncio.windows_events import NULL
from doctest import OutputChecker
from socket import *
from time import sleep
from tracemalloc import start
from turtle import left
import struct
import os
import datetime
from threading import Timer
import random

# 下面这些是全局的内容，不会进行更改，但是在不同的报文之间是有变化的
HOST='84.32.244.208'
PORT=502
BUFSIZE=1024
ADDRESS=(HOST,PORT)
tcpClientSocket=socket(AF_INET,SOCK_STREAM)
tcpClientSocket.setsockopt(SOL_SOCKET,SO_KEEPALIVE,True)
tcpClientSocket.ioctl(SIO_KEEPALIVE_VALS,
                (1,     # 开启保活机制
                60*1000,    # 1分钟后如果对方没有反应，开始探测连接是否存在
                30*1000)    # 30分钟探测一次，默认探测10次，失败则断开
            )
# tcpClientSocket.settimeout(2)
tcpClientSocket.connect(ADDRESS)

# trasactionID=random.randint(1000,20000) # 这个值用于标识每一次modbus的请求与响应报文，这里初始化为b'\x39\xcd'
trasactionID=2022
protocol_id=b'\x00\x00'
Length=0
unit_id=b'\x00'
schneider_untiy=b'\x5a'  
FunctionCode={"init_comm":b'\x01',"read_id":b'\x02',"read_project_info":b'\x03',"read_plc_info":b'\x04',"repeat":b'\x0a',"take_plc_reservation":b'\x10',\
    "release_reservation_plc":b'\x11',"keep_alive":b'\x12',"read_mem_block":b'\x20',"initialize_upload":b'\x30',"upload_block":b'\x31',\
    "end_stategy_upload":b'\x32',"initialize_download":b'\x33',"download_block":b'\x34',"end_stretegy_download":b'\x35',\
    "start_plc":b'\x40',"stop_plc":b'\x41'}
sessionID=b'\x00' # sessionID对于每一次连接建立的过程而言都是从00开始的，然后由于请求报文的出现，这个出现了变化

def SendPrint(trasactionID,start):  # 这个函数的作用在于发包和打印信息
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
    '''
    bytebuff=bytes(data)
    for b in range(len(bytebuff)):   # 核对信息
        print("%02x"%(bytebuff[b]))
    print(data)
    '''
    return trasactionID,data  # 由于每一次发送之后的回应报文都是需要匹配上的

def PrintInfo(data):
    bytebuff=bytes(data)
    for b in range(len(bytebuff)):   # 核对信息
        print("%02x"%(bytebuff[b]),end=' ')
    print(data)

def generate_number(): # 用于生成第二次的同步报文内容
    data=b''
    i=0
    while i<1017:
        data+=int.to_bytes(i%256,length=1,byteorder='little',signed=False)
        i+=1
    return data

process_flow={1:["read_id"],\
              2:["init_comm",b'\x00'],\
              3:['repeat',b'\x00'+b'\x54'*1017],\
              4:["read_project_info",b'\x00'],\
              5:["read_project_info",b'\x04'],\
              6:['read_plc_info'],\
              7:['repeat',b'\x00'+generate_number()],\
              8:['read_plc_info'],\
              9:['read_plc_info'],\
              10:['read_mem_block',b'\x01\x13\x00\x00\x00\x00\x00\x00\x01'],\
              11:['read_mem_block',b'\x01\x14\x00\x00\x00\x00\x00\x00\x02'],\
              12:['read_mem_block',b'\x01\x14\x00\x00\x00\x00\x00\x00\x03'],\
              13:['read_mem_block',b'\x01\x13\x00\x00\x00\x00\x00\x00\x01'],\
              # 后续还需要检查对于不同的工程，是不是在同一块区域
              14:['take_plc_reservation',b'\xc0\x1e\x00\x00\x0f\x4c\x41\x50\x54\x4f\x50\x2d\x43\x32\x4a\x47\x4c\x48\x48\x31'],\
              # 注释在14号报文的前两个字节经过测试，随机生成，可以通过connect，
              15:['read_plc_info'],\
              # 为了能够获取到需要的报文，这里再次发一个报文
              16:['start_plc',b'\xff\x00'],\
              17:['stop_plc',b'\xff\x00'],\
              18:['release_reservation_plc']
                     }

if __name__=="__main__":
    # 按照通信的过程中这里是三次握手后的第一个报文，需要read_id
    count=14  # 当这个数为14时，可以直接启动工程，当为17时用于关闭工程
    while count==14:  # 仅用于测试当只有一个0x10报文的反应情况
    #while True:
        try:
            funcCode=process_flow[count][0]
            if len(process_flow[count]) >1:
                more=process_flow[count][1]
                start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
                    int(4+len(bytes(more))).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
                    +schneider_untiy+sessionID+FunctionCode[funcCode]+more
            else:
                start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
                    int(4).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
                    +schneider_untiy+sessionID+FunctionCode[funcCode]
            if funcCode=='repeat':
                print(funcCode)
                HaveReceived=0
                WishReceived=1028
                packetdata=b''
                tcpClientSocket.send(start)  #发包过程
                trasactionID+=1
                while HaveReceived < WishReceived:
                    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
                    packetdata+=bytes(data)
                    HaveReceived+=len(bytes(data))
                # 通过抓包分析repeat报文的接收报文长度就是1028bits，所以这里需要另外对大小进行计算，然后使得能够进行处理
                count+=1
            else:
                print(funcCode)
                tcpClientSocket.send(start)  #发包过程
                trasactionID+=1
                data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
                if funcCode=='take_plc_reservation':
                    bytebuff=bytes(data)
                    sessionID=int(bytebuff[-1]).to_bytes(length=1, byteorder='big', signed=False)
                if not data:
                    print("There is no data received!!!")
                    break
                else:
                    pass
                count+=1 
        except:
            break
    tcpClientSocket.close()