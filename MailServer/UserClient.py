import socket
import random

import conmysql


class UserClient:

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = -1

    def connect(self,hostip):
        port = -1
        while port == -1:
            user_name = input("请输入用户名:\n")
            port = conmysql.port_find(user_name)
            if port == -1:
                print("用户名不存在，请重新输入")
        print("请选择发信还是收信服务(1.发信    2.收信)")
        choose = input()
        while choose != '1' and choose != '2':
            print("输入错误，请重新选择")
            choose = input()
        if choose == '1':
            port = port
        else:
            port = port + 1
        self.client_socket.connect((hostip,port))
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