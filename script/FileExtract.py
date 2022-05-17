'''
    # 该文件用于提取PLC中的文件，对于功能码的重放目前是正确的
'''
from doctest import OutputChecker
from socket import *
from time import sleep
from turtle import left
import struct
import os
import datetime
from threading import Timer


# 下面这些是全局的内容，不会进行更改，但是在不同的报文之间是有变化的
HOST='84.32.244.208'
PORT=502
BUFSIZE=1028   # 🤦‍♂️这里还是有问题，似乎太大了之后有一些报文就要连续收两次才能将报文完全接收完毕
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
FunctionCode={"init_comm":b'\x01',"read_id":b'\x02',"read_project_info":b'\x03',"read_plc_info":b'\x04',"read_card_info":b'\x06',\
    "repeat":b'\x0a',"take_plc_reservation":b'\x10',"release_reservation_plc":b'\x11',"keep_alive":b'\x12',"read_mem_block":b'\x20',\
    "initialize_upload":b'\x30',"upload_block":b'\x31',"end_stategy_upload":b'\x32',"initialize_download":b'\x33',"download_block":b'\x34',\
    "end_stretegy_download":b'\x35',"start_plc":b'\x40',"stop_plc":b'\x41',"reading_sys_bits":b'\x50'}
sessionID=b'\x00' # sessionID对于每一次连接建立的过程而言都是从00开始的，然后由于请求报文的出现，这个出现了变化

def SendPrint(trasactionID,start):  # 这个函数的作用在于发包和打印信息
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
    bytebuff=bytes(data)
    for b in range(len(bytebuff)):   # 核对信息
        print("%02x"%(bytebuff[b]))
    print(data)
    return trasactionID,data  # 由于每一次发送之后的回应报文都是需要匹配上的


if __name__=="__main__":
    filehandle=open("./DownloadedFile.apx","wb")  # 这里应该是用的二进制写入文件
    # 首先先来一个更改session ID的过程
    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(24).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        + schneider_untiy+sessionID+FunctionCode['take_plc_reservation'] + \
        b'\xc0\x1e\x00\x00\x0f\x4c\x41\x50\x54\x4f\x50\x2d\x43\x32\x4a\x47\x4c\x48\x48\x31'   # 初始化下载的功能，\x33
    print(start)
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
    print(data)
    bytebuff=bytes(data)
    sessionID=int(bytebuff[-1]).to_bytes(length=1, byteorder='big', signed=False)
    print("~~~~~~~~")
    os.system("pause")
    '''
    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(8).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+sessionID+FunctionCode['reading_sys_bits']+b'\x15\x00\x01\x0b'   
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)

    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(8).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+sessionID+FunctionCode['reading_sys_bits']+b'\x15\x00\x01\x07'   
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)

    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(5).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+b'\x00\x03\x01'   
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)

    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(5).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+b'\x00\x06\x00'   
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)

    some=[b'\x00\x20\x01\x13\x00\x00\x00\x00\x00\x00\x01',
        b'\x00\x20\x01\x14\x00\x00\x00\x00\x00\x00\x02',
        b'\x00\x20\x01\x14\x00\x00\x02\x00\x00\x34\x03',
    ]
    for i in some:
        start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
            int(13).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
            +schneider_untiy+i   
        tcpClientSocket.send(start)  #发包过程
        trasactionID+=1
        data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)

    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(7).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+b'\x00\x07\x00\x36\x00'   
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)


    somefothis=[b'\x00\x00',b'\xf7\x03',b'\xee\x07',b'\xe5\x0b',b'\xdc\x0f',b'\xd3\x13',b'\xca\x17']
    for i in somefothis:
        start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
            int(13).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
            +schneider_untiy+b'\x00'+FunctionCode['read_mem_block']+b'\x01\x36\x00'+i+b'\x00\x00\xf7\x03'   
        tcpClientSocket.send(start)  #发包过程
        trasactionID+=1
        sleep(0.5)
        data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)

    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(13).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+b'\x00'+FunctionCode['read_mem_block']+b'\x01\x36\x00'+b'\xc1\x1b'+b'\x00\x00\x58\x00'   
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    sleep(0.5)
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)

    for i in some:
        start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
            int(13).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
            +schneider_untiy+i   
        tcpClientSocket.send(start)  #发包过程
        trasactionID+=1
        data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
    '''
    # FunctionID :0x33
    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(8).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+sessionID+FunctionCode['initialize_download']+b'\x00\x01\xfb\x03'# 初始化下载的功能，\x33
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
    bytebuff=bytes(data)
    for b in range(len(bytebuff)):   # 核对信息
        print("%02x"%(bytebuff[b]),end=' ')
    print("")
    print(data)
    # FunctionID :0x34
    Block=1
    while Block<=57:  # 😢实验证明，只要是最后一个0x34和0x35一致，0x35就会正确返回，而不是去做内容的校验
        print("Block #%d"%Block)
        Tobesent=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
            int(8).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
            +schneider_untiy+sessionID+FunctionCode['download_block']+b'\x00\x01'+int(Block).to_bytes(length=1, \
            byteorder='little', signed=False)+b'\x00'
        '''
        for b in range(len(Tobesent)):   # 核对信息
            print("%02x"%(Tobesent[b]))
        print("\n")  
        '''
        tcpClientSocket.send(Tobesent)  #发包过程
        data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
        trasactionID+=1
        filehandle.write(data)
        print("length:%d"%len(bytes(data)))
        Block+=1
        bytebuff=bytes(data)
        for b in range(len(bytebuff)):   # 核对信息
            print("%02x"%(bytebuff[b]),end=' ')
        print("")
        print(data)
    
    # FunctionID :0x35
    start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+protocol_id+\
        int(8).to_bytes(length=2, byteorder='big', signed=False)+unit_id\
        +schneider_untiy+sessionID+FunctionCode['end_stretegy_download']+b'\x00\x01'+int(Block-1).to_bytes(length=1, \
        byteorder='little', signed=False)+b'\x00'  


    print("~~~~~~~~~")
    tcpClientSocket.send(start)  #发包过程
    trasactionID+=1
    data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
    bytebuff=bytes(data)
    for b in range(len(bytebuff)):   # 核对信息
        print("%02x"%(bytebuff[b]),end=' ')
    print("")
    print(data)

    filehandle.close()
    tcpClientSocket.close()
    sleep(3)
    # os.system("pause")
    
    
