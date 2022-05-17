'''
    # 该文件可以做到在使用编程环境连接设备后启动或者停止项目，但是没有办法将连接过程也很好的仿真
'''

from socket import *
from time import sleep

HOST='84.32.244.208'
PORT=502
BUFSIZE=1024
ADDRESS=(HOST,PORT)
tcpClientSocket=socket(AF_INET,SOCK_STREAM)
tcpClientSocket.connect(ADDRESS)
trasactionID=2022
sessionID=b'\x3e'  # 每一次只需要更改这里即可
reuse_session=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x18\x00\x5a\x00\x10'+b'\xc0\x1e\x00\x00\x0f\x4c\x41\x50\x54\x4f\x50\x2d\x43\x32\x4a\x47\x4c\x48\x48\x31'
tcpClientSocket.send(reuse_session)     
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
trasactionID+=1
bytebuff=bytes(data)
sessionID=int(bytebuff[-1]).to_bytes(length=1, byteorder='big', signed=False)
start=b'\x3a\xa6\x00\x00\x00\x06\x00\x5a'+sessionID+b'\x40\xff\x00'  
tcpClientSocket.send(start)
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
# print(data)
sleep(2)
stop=b'\x3a\xa6\x00\x00\x00\x06\x00\x5a'+sessionID+b'\x41\xff\x00' 
tcpClientSocket.send(stop)
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
# print(data)
tcpClientSocket.close()