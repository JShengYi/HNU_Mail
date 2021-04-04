import socket
import random

# from MailService import conmysql
# from MailService import UserServer
import conmysql
import UserServerc
from multiprocessing import Process


class MailServer(object):
    def __init__(self,):
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def bind(self, port):
        self.server_socket.bind(("",port))

    def start(self):
        self.server_socket.listen(128)
        while True:
            client_socket, client_address = self.server_socket.accept()
            print("[%s,%s]用户已连接" % client_address)
            # port = int(client_address[1])
            # # 端口号为12345为客户端登录注册服务连接
            # if port == 12345 :
            #     handle_client_process = Process(target=self.handle_client, args=(client_socket,))
            #     handle_client_process.start()
            # # 端口号为12346为客户端的管理服务连接
            # elif port == 12346 :
            handle_client_process = Process(target=self.handle_manager, args=(client_socket,))
            handle_client_process.start()
            # else:
            #      client_socket.send("Your service is stopped!".encode("utf-8"))

    #客户端管理服务
    def handle_manager(self,client_socket):
        login_state = 0  # 记录管理员认证状态

        while True:
            request_data = client_socket.recv(1024)
            str_data = request_data.decode("utf-8")
            if str_data == "QUIT":
                break
            print(str_data)
            sstr = str_data.split(" ")
            if sstr[0] == "login" and len(sstr) == 3:
                try:
                    user_name = sstr[1]
                    user_code = sstr[2]
                    # 进行用户信息校验
                    if user_name=="admin" and user_code=="123456":
                        login_state=1;
                        msg= "OK : login succeed!"
                    else:
                        msg= "Error : login error!"
                except IOError:
                    msg= "Error : input error!"
            elif sstr[0] == "manage" and len(sstr) == 4:
                try:
                    start_stop = sstr[1]
                    smtp_pop = sstr[2]
                    user_name = sstr[3]
                    if login_state==0:
                        msg = "Error : authority error!"
                    else:
                        msg= "OK : manage succeed!"
                        if start_stop == "start":
                            if smtp_pop == "smtp":
                                conmysql.start_smtp(user_name)
                            else:
                                conmysql.start_pop(user_name)
                        else :
                            if smtp_pop == "smtp":
                                conmysql.stop_smtp(user_name)
                            else:
                                conmysql.stop_pop(user_name)
                except IOError:
                    msg= "Error : input error!"
            elif sstr[0] == "list" and len(sstr) == 1:
                try:
                    if login_state==0:
                        msg = "Error : authority error!"
                    else:
                        info = conmysql.info_userandport()
                        response = ""
                        for i in info:
                            response += str(i[0])
                            response += " "
                            response += str(i[1])
                            response += " "
                            response += str(i[2])
                            response += "\n"
                        response += "."
                        msg =response
                except IOError:
                    msg= "Error : input error!"
            client_socket.send(msg.encode("utf-8"))
        #关闭客户端连接
        client_socket.close()

    # 客户端登录注册服务
    def handle_client(self,client_socket):
        while True:
            request_data = client_socket.recv(1024)
            str_data = request_data.decode("utf-8")
            if str_data == "QUIT":
                break
            print(str_data)
            msg = self.command_analyze(str_data)
            client_socket.send(msg.encode("utf-8"))
        #关闭客户端连接
        client_socket.close()

    def command_analyze(self,str_data):
        sstr = str_data.split(" ")
        if sstr[0] == "register" and len(sstr) == 4:
            try:
                user_name = sstr[1]
                user_code = sstr[2]
                port = sstr[3]
                if port == "58000" :
                    user_email = user_name + "@qq.com"
                else:
                    user_email = user_name + "@163.com"
                #将用户的信息存入数据库
                conmysql.register(user_name,user_code,port,user_email)
                mailadd = user_name
                return "OK : register succeed!\n mailaddr ="+mailadd
            except IOError :
                return "Error : input error!"
        elif sstr[0] == "login" and len(sstr) == 4:
            try:
                user_name = sstr[1]
                user_code = sstr[2]
                # 进行用户信息校验
                if conmysql.user_identified(user_name, user_code) == 1:
                    return "OK : login succeed!"
                else :
                    return "Error : login error!"
            except IOError:
                return "Error : input error!"
        else:
            return "Error : input error!"


if __name__ == '__main__':
    mailServer = MailServer()
    mailServer.bind(7001)
    mailServer.start()




