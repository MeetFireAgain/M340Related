"""
    该文件用于对于Modbus一些原始功能码使用，读取寄存器或者是线圈等
"""

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
# 虽然都是有输出的，但是都是零，且都是一样的，可能是由于工程中没有一些太多初始化的变量的原因导致这样的结果

coil_poll_0x01=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x06\x01\x04\x00\x07\x00\x18' #读输入寄存器的操作 
tcpClientSocket.send(coil_poll_0x01)
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
print(data)
trasactionID+=1

coil_poll_0x02=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x06\x01\x04\x00\x07\x00\x18' #读输入寄存器的操作 
tcpClientSocket.send(coil_poll_0x02)
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
print(data)
trasactionID+=1

coil_poll_0x03=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x06\x01\x04\x00\x07\x00\x18' #读输入寄存器的操作 
tcpClientSocket.send(coil_poll_0x03)
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
print(data)
trasactionID+=1

coil_poll_0x04=int(trasactionID).to_bytes(length=2, byteorder='big', signed=False)+\
    b'\x00\x00\x00\x06\x01\x04\x00\x07\x00\x18' #读输入寄存器的操作 
tcpClientSocket.send(coil_poll_0x04)
data,ADDR=tcpClientSocket.recvfrom(BUFSIZE)
print(data)

