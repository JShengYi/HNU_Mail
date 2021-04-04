import socket
import base64
import time
import random

import conmysql
# from MailService import conmysql
from multiprocessing import Process


class UserServer(object):
    def __init__(self,):
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.port = -1

    def bind(self, port):
        self.server_socket.bind(("",port))
        self.port = int(port)

    def start(self):
        self.server_socket.listen(128)
        while True:
            #查询服务状态
            print(self.port)

            client_socket, client_address = self.server_socket.accept()
            print("[%s,%s]用户已连接" % client_address)
            # port = int(client_address[1])
            # # 端口号为50000到59999为服务器连接
            # if port >= 50000 and port <= 59999:
            #     handle_server_process = Process(target=self.smtpMailRecv, args=(client_socket,client_address,))
            #     handle_server_process.start()
            # # 端口号为40000到49999为客户端的SMTP连接
            # elif port >= 40000 and port <= 49999 :
            #     handle_client_process = Process(target=self.handle_client_smtp, args=(client_socket,client_address,))
            #     handle_client_process.start()
            # #端口号为30000到39999为客户端的POP连接
            # elif port >= 30000 and port <= 39999 :
            handle_client_pop = Process(target=self.handle_client_pop,args = (client_socket,client_address,))
            handle_client_pop.start()
            # else:
            #      client_socket.send("Your service is stopped!".encode("utf-8"))

    #客户端到服务器的SMTP服务
    def handle_client_smtp(self,client_socket,client_address):
        welcome_state = 0 #欢迎状态
        login_state = 0 #记录用户认证状态
        source_state = 0 #记录是否填写邮件双方
        subject_state = 0 #记录是否填写邮件主题
        des_state = 0 #记录是否填写邮件双方
        mail_cont = ""#记录邮件内容
        mail_subject = ""#记录邮件主题
        mail_source = "" #记录信的来源
        mail_des = "" #记录信的去处

        while True:
            request_data = client_socket.recv(1024)
            str_data = request_data.decode("utf-8")
            print("From:[%s,%s]"%client_address,end=" ")
            print(str_data)
            sstr = str_data.split(" ")
            try:
                if sstr[0] == "EHLO":
                    response = "250-smtp.qq.com\n" \
                               "250-PIPELINING\n" \
                               "250-STARTTLS\n" \
                               "250-AUTH LOGIN PLAIN\n" \
                               "250-AUTH=LOGIN\n"\
                               "250-MAILCOMPRESS\n"\
                               "250 8BITMIME!"
                    welcome_state = 1   #可以进行用户认证
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "DATA" and len(sstr) == 1 and des_state == 1 and source_state == 1 and subject_state == 1:
                    response = "354 Enter mail,end with '.' on a line by itself!"
                    client_socket.send(response.encode("utf-8"))
                    while True:
                        recv_data = client_socket.recv(1024)
                        strr = recv_data.decode("utf-8")
                        print(strr)
                        if strr == '.':
                            break
                        else:
                            reply = "$$"
                            client_socket.send(reply.encode("utf-8"))
                        mail_cont += strr
                        mail_cont += "$$"

                    # 拼接信的内容
                    mail = {}
                    mail['From'] = mail_source
                    mail['To'] = mail_des
                    mail['Subject'] = mail_subject
                    mail['Cont'] = mail_cont
                    mail_cont = " " #刷新mail_cout 避免连续发信内容叠加
                    self.smtpMailDeliver(mail)

                    response = "250 ok!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "QUIT":
                    # 关闭客户端连接
                    break
                elif sstr[0] + sstr[1] == "AUTHLOGIN" and welcome_state == 1 and len(sstr) == 2:
                    #用户名认证
                    response = "username=!"
                    # response = base64.b64encode(str.encode("utf-8"))
                    client_socket.send(response.encode("utf-8"))
                    recv_data = client_socket.recv(1024)
                    # username = base64.b64decode(recv_data).decode("utf-8")
                    username = recv_data.decode("utf-8")
                    print("From:[%s,%s]" % client_address, end=" ")
                    print(username)

                    #用户密码认证
                    response = "Password=!"
                    # response = base64.b64encode(str.encode("utf-8"))
                    client_socket.send(response.encode("utf-8"))
                    recv_data = client_socket.recv(1024)
                    # password = base64.b64decode(recv_data).decode("utf-8")
                    password = recv_data.decode("utf-8")
                    print("From:[%s,%s]" % client_address, end=" ")
                    print(password)

                    #服务校验
                    state = conmysql.state_port(username)
                    print(state)
                    smtp_state = state[0]
                    pop_state = state[1]

                    #用户名密码数据库验证
                    if conmysql.user_identified(username,password) == 1 and smtp_state=='1':
                        response = "235 auth successfully!"#认证成功
                        login_state = 1
                    else:
                        if conmysql.user_identified(username,password) == 1:
                            response = "535 auth failed!" #认证失败
                        else:
                            response = "536 smtp failed!" #smtp服务被禁用
                    client_socket.send(response.encode("utf-8"))

                elif sstr[0] + sstr[1] == "MAILFROM:" and len(sstr) == 3 and login_state ==1:
                    mail_source = sstr[2]
                    source_state = 1
                    response  =  "250 ok!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] + sstr[1] == "RCPTTO:" and len(sstr) == 3 and login_state ==1:
                    mail_des = sstr[2]
                    des_state = 1
                    response = "250 ok!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "SUBJECT:" and login_state == 1:
                    sentence = sstr[1:]
                    for i in sentence:
                        mail_subject += i
                        mail_subject += " "
                    subject_state = 1
                    response = "250 ok!"
                    client_socket.send(response.encode("utf-8"))
                else:
                    response = "502 Error: command not implemented!"
                    client_socket.send(response.encode("utf-8"))
            except IndexError:
                response = "502 Error: command not implemented!"
                client_socket.send(response.encode("utf-8"))

        #关闭客户端连接
        client_socket.close()



    #客户端到服务器的POP服务
    def handle_client_pop(self,client_socket,client_address):
        login_state = 0 #记录用户登录状态
        user_name = "" #记录用户名
        pass_word = "" #记录密码
        while True:
            request_data = client_socket.recv(1024)
            str_data = request_data.decode("utf-8")
            print("From:[%s,%s]"%client_address,end = " ")
            print(str_data)
            sstr = str_data.split(" ")
            try:
                if sstr[0] == "USER" and len(sstr) == 2:
                    user_name= sstr[1]
                    response = "+OK!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "PASS" and len(sstr) == 2:
                    pass_word = sstr[1]
                    #服务校验
                    state = conmysql.state_port(user_name)
                    print(state)
                    smtp_state = state[0]
                    pop_state = state[1]
                    if conmysql.user_identified(user_name,pass_word) == 1 and pop_state == '1':
                        #认证成功
                        response = "+OK user successfully logged on!"
                        login_state = 1
                    else:
                        if conmysql.user_identified(user_name,pass_word) != 1:
                        #认证失败
                            response = "-ERR user identify failed!"
                        else :
                            #pop被禁用
                            response = "-ERR user pop failed!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "LIST" and len(sstr) == 1 and login_state == 1:
                    info = conmysql.list_email(user_name+"@qq.com")
                    response = ""
                    for i in info:
                        response += str(i[0])
                        response += " "
                        response += str(i[1])
                        response += " "
                        response += str(i[2])
                        response += "\n"
                    response += ".!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "RETR" and len(sstr) == 2 and login_state == 1:
                    li_id = int(sstr[1])
                    cont = conmysql.cont_email(user_name+"@qq.com",li_id)
                    if cont == -1:
                        response = "-ERR input email id doesn't exist!"
                    else:
                        response = cont+"!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "DELE" and len(sstr) == 2 and login_state == 1:
                    del_id = int(sstr[1])
                    conmysql.dele_mail(user_name+"@qq.com",del_id)
                    response = "+OK!"
                    client_socket.send(response.encode("utf-8"))
                elif sstr[0] == "QUIT" and len(sstr) == 1:
                    response = "+OK POP3 server signing off!"
                    client_socket.send(response.encode("utf-8"))
                    break
                else:
                    response = "-ERR Unknown command!"
                    client_socket.send(response.encode("utf-8"))
            except IndexError:
                response = "-ERR Unknown command!"
                client_socket.send(response.encode("utf-8"))
        #关闭客户端
        client_socket.close()

    #服务器发送邮件到服务器
    def smtpMailDeliver(self,mail):
        print(mail)
        mail_des = mail['To']
        hostip = "127.0.0.1"
        port = conmysql.des_port(mail_des)  # 另一个服务器程序的端口号
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flag = 0
        while flag != 1:
            try:
                cli_port = random.randint(50000, 59999)
                client_socket.bind(("", cli_port))
                flag = 1
                print(cli_port)
            except socket.error:
                print("端口号被占用")
                flag = 0
        i = 0
        while i != 1:
            try:
                client_socket.connect((hostip, port))
                i = 1
            except socket.error:
                print("目的服务器程序未启动")
                time.sleep(1800)
        client_socket.send(str(mail).encode("utf-8"))
        client_socket.close()


    #服务器接收从服务器发送而来的邮件
    def smtpMailRecv(self,client_socket,client_address):
        mail_data = client_socket.recv(1024)
        print("From:[%s,%s]" % client_address, end=" ")
        print(mail_data.decode("utf-8"))
        mail = eval(mail_data.decode("utf-8"))
        response = "250 ok!"
        client_socket.send(response.encode("utf-8"))
        #将邮件存入数据库中
        conmysql.save_mail(mail)



if __name__ == '__main__':
    mailServer = UserServer()
    mailServer.bind(58001)
    mailServer.start()




