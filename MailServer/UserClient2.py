import socket
import random

import conmysql


class UserClient:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = -1

    def connect(self,hostip):
        port = 7000
        # self.client_socket.connect((hostip,port))
        inp = input("请输入功能:\n")
        if inp == "1":
            port = 7000
        else:
            port = 7001
        self.client_socket.connect((hostip, port))
        print("连接服务器成功")

    def start(self):
        while True:
            sendmsg = input()
            # sdmsg = "["+str(self.ip) + "," + str(self.port) + "]" + sendmsg
            self.client_socket.send(sendmsg.encode("utf-8"))
            if sendmsg == "QUIT":
                break
            recv_data = self.client_socket.recv(1024)
            if recv_data.decode("utf-8") != "$$":
                print("From Server:",recv_data.decode("utf-8"))

        #关闭与服务器的连接
        self.client_socket.close()


def main():
    user_client = UserClient()
    user_client.connect("127.0.0.1")
    user_client.start()

if __name__ == '__main__':
    main()