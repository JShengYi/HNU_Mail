import pymysql
import time

#数据库连接
def connectdb():
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user':'root',
        'password': '123456',
        'database': 'mailsystem',
        'charset': 'utf8',

    }
    con = pymysql.connect(**config)
    return con


#用户注册
def register(user_name,user_code,port,user_email):
    con = connectdb()
    cursor = con.cursor()
    port2 =int(port)
    sql = "INSERT INTO user(username,usercode,useremail,smtp_state,pop_state,port) VALUES('%s','%s','%s','%s','%s','%d')"
    data = (user_name,user_code,user_email,"1","1",port2)
    cursor.execute(sql%data)
    con.commit()
    cursor.close()
    con.close()


#用户认证
def user_identified(user_name,user_code):
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT usercode FROM user where username = '%s'"
    data = (user_name,)
    cursor.execute(sql%data)
    code = " "
    try:
        for row in cursor.fetchall():
            code = row[0]
    except IndexError:
        return 0
    cursor.close()
    con.close()

    if code == user_code:
        return 1
    else:
        return 0


#从用户的邮箱地址查询出用户的端口号
def des_port(user_mail):
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT port FROM user where useremail = '%s'"
    data = (user_mail,)
    cursor.execute(sql%data)
    port = -1
    for row in cursor.fetchall():
        port = row[0]
    cursor.close()
    con.close()
    return port


#将邮件存入数据库
def save_mail(mail):
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT COUNT(*) FROM email where email_to = '%s'"
    data = (mail['To'],)
    cursor.execute(sql%data)
    num = -1
    try:
        for row in cursor.fetchall():
            num = row[0] + 1
    except IndexError:
        num = 1
    # print(num)
    mail_size = len(mail['Cont'])
    sql = "INSERT INTO email(email_no,email_from,email_to,email_subject,email_cont,time,email_size) VALUES('%d','%s','%s','%s','%s','%s','%d')"
    recv_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    content = mail['Cont'].split("$$")
    mail_cont = ""
    for i in range(len(content)):
        mail_cont += content[i]
        if i != len(content)-1:
            mail_cont += "\n"
    data = (num,mail['From'],mail['To'],mail['Subject'],mail_cont,recv_time,mail_size)
    cursor.execute(sql%data)
    con.commit()
    cursor.close()
    con.close()

#将邮箱中对应用户的信件提取出来
def list_email(user_name):
    info = []
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT email_no,email_subject,time FROM email where email_to = '%s'"
    data = (user_name ,)
    cursor.execute(sql%data)
    for row in cursor.fetchall():
        info.append(row)
    #print(info)
    cursor.close()
    con.close()
    return info

#读取对应参数的邮件
def cont_email(user,id):
    useremailaddr = user
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT email_cont from email where email_to = '%s' and email_no = '%d'"
    data = (useremailaddr,id)
    cursor.execute(sql%data)
    cont = ""
    try:
        for row in cursor.fetchall():
            cont = row[0]
    except IndexError:
        return -1
    print(cont)
    cursor.close()
    con.close()
    return cont

#删除邮件
def dele_mail(user,id):
    user_email = user
    con = connectdb()
    cursor = con.cursor()
    sql = "DELETE FROM email where email_no = '%d' and email_to = '%s'"
    data = (id,user_email)
    cursor.execute(sql%data)
    con.commit()
    cursor.close()
    con.close()
    return 0

#根据用户名查找出端口号
def port_find(user_name):
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT port FROM user WHERE username = '%s'"
    data = (user_name,)
    cursor.execute(sql % data)
    port = -1
    try:
        for row in cursor.fetchall():
            port = int(row[0])
    except IndexError:
        port = -1
    cursor.close()
    con.close()
    return port

#管理用户的smtp和pop3的状态码
def stop_smtp(user):
    con = connectdb()
    cursor = con.cursor()
    sql = "UPDATE user SET smtp_state = '%s' where username = '%s'"
    data = ('0',user,)
    cursor.execute(sql%data)
    con.commit()
    cursor.close()
    con.close()
    return user + " smtp服务停止"

def stop_pop(user):
    con = connectdb()
    cursor = con.cursor()
    sql = "UPDATE user SET pop_state = '%s' where username = '%s'"
    data = ('0', user,)
    cursor.execute(sql % data)
    con.commit()
    cursor.close()
    con.close()
    return user + " pop服务停止"

def start_smtp(user):
    con = connectdb()
    cursor = con.cursor()
    sql = "UPDATE user SET smtp_state = '%s' where username = '%s'"
    data = ('1', user,)
    cursor.execute(sql % data)
    con.commit()
    cursor.close()
    con.close()
    return user + " smtp服务开启"


def start_pop(user):
    con = connectdb()
    cursor = con.cursor()
    sql = "UPDATE user SET pop_state = '%s' where username = '%s'"
    data = ('1', user,)
    cursor.execute(sql % data)
    con.commit()
    cursor.close()
    con.close()
    return user + " pop服务开启"

#通过端口号查询smtp和pop3服务的启停
def state_port(user):
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT smtp_state, pop_state FROM user where username = '%s'"
    data = (user,)
    cursor.execute(sql%data)
    state = []
    for row in cursor.fetchall():
        state.append(row[0])
        state.append(row[1])
    #print(state)
    return state

#返回所有用户名
def info_user():
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT username FROM user"
    cursor.execute(sql)
    user = []
    for row in cursor.fetchall():
        user.append(row[0])
    #print(user)
    cursor.close()
    con.close()
    return user

#列举出用户名和服务状态
def info_userandport():
    con = connectdb()
    cursor = con.cursor()
    sql = "SELECT username,smtp_state,pop_state from user"
    cursor.execute(sql)
    info = []
    for row in cursor.fetchall():
        info.append(row)
    return info

def update_password(user,password):
    con = connectdb()
    cursor = con.cursor()
    sql = "UPDATE user SET usercode = '%s' where username = '%s'"
    data = (password, user,)
    cursor.execute(sql % data)
    con.commit()
    cursor.close()
    con.close()
    return 1


if __name__ == '__main__':
    # register("alice555","ccc123",39919)
    # print(user_identified("alice555", "ccc123"))
    # print((des_port("alice555@wsl.com")))
    # mail = {
    #     'To':'bob@wsl.com',
    #     'From': 'wow54@wsl.com',
    #     'Subject':'I show',
    #     'Cont':'haihaihai, I like uuu',
    # }
    # save_mail(mail)
    # list_email("ai")
    # cont_email("bob",1)
    # dele_mail("ccc456",2)
    # s = start_pop("alice555")
    # print(s)
    # state_port(54004)
    # info_user()
    # print(info_userandport())
    # stop_pop("ccc456")
    update_password("jsy","1234")