'''
    # 该文件用于专门对两个比较复杂的功能码(0x36)进行测试
'''
from socket import *
from time import sleep

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
tcpClientSocket.connect(ADDRESS)
trasactionID=2022
sessionID=b'\x7a'  # 每一次只需要更改这里即可

def Printing(data):
    bytebuff=bytes(data)
    for b in range(len(bytebuff)):   # 核对信息
        print("%02x"%(bytebuff[b]),end=' ')
    print("")
    print(data)

# 用于更新Session ID
reuse_session=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x18\x00\x5a\x00\x10'+b'\xc0\x1e\x00\x00\x0f\x4c\x41\x50\x54\x4f\x50\x2d\x43\x32\x4a\x47\x4c\x48\x48\x31'
tcpClientSocket.send(reuse_session)      #0x19,测试成功
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
Printing(data)
trasactionID+=1
bytebuff=bytes(data)
sessionID=int(bytebuff[-1]).to_bytes(length=1, byteorder='big', signed=False)

start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x07\x00\x5a'+sessionID+b'\x36\x01\x00\x00'
tcpClientSocket.send(start)     
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
trasactionID+=1
Printing(data)

start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x07\x00\x5a'+sessionID+b'\x36\x02\x00\x00'
tcpClientSocket.send(start)     
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
trasactionID+=1
Printing(data)

start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x07\x00\x5a'+sessionID+b'\x36\x03\x00\x00'
tcpClientSocket.send(start)     
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
trasactionID+=1
Printing(data)

# 0x04测试失败，但是这个在原先的过程中就是会失败的
start=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x07\x00\x5a'+sessionID+b'\x36\x04\x00\x00'
tcpClientSocket.send(start)     
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
trasactionID+=1
Printing(data)

tcpClientSocket.close()