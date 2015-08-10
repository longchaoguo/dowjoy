# -*- coding: utf-8 -*-

import fileinput
import time
import datetime  
import string
import smtplib,sys
import email
import mimetypes
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from email.mime.audio import MIMEAudio
'''
     邮件收发管理
'''
reload(sys)
sys.setdefaultencoding('utf8')
#发送服务器信息
smtpserver='mail.downjoy.com'  
smtpuser='webmaster@downjoy.com'  
smtppass='bourne@8.3'
smtpport='25'
logPath="/usr/local/apache/logs/accesslog"
#/usr/local/apache/logs/accesslog
def login():
    '''
        发件人登录到服务器
    '''
    server=smtplib.SMTP(smtpserver,smtpport)  
    server.ehlo()  
    server.login(smtpuser,smtppass)  
    return server

def sendTextEmail(toAdd,subject,content):
    '''
        功能：发送纯文本邮件
        参数说明：
        toAdd:收件人E-mail地址    类型：list
        subject:主题，类型:string
        content:邮件内容    类型：string
        fromAdd:发件人，默认为服务器用户
        返回值：True/False
    '''
    result = False
    server = login()
    msg = Message()
    msg['Mime-Version']='1.0'  
    msg['From']    = smtpuser  
    msg['To']      = toAdd  
    msg['Subject'] = subject  
    msg['Date']    = email.Utils.formatdate()          # curr datetime, rfc2822  
    msg.set_payload(content)
    try:      
        server.sendmail(smtpuser,toAdd,str(msg))   # may also raise exc  
        result = True
    except Exception ,ex:  
        print Exception,ex  
        print 'Error - send failed'  
        
    return result
def addPv():
    now = datetime.datetime.now()  
    date = now - datetime.timedelta(days = 1)
    t=date.strftime('%y%m%d')
    mt=date.strftime('20%y年%m月%d日')
    print mt,
#    t=time.strftime('%y%m%d')
    
    f = open(logPath+"/zt_ex"+t+".log")             # 返回一个文件对象
    v="a140403qingmingjie"
    i=0
    line = f.readline()             # 调用文件的 readline()方法
    while line:
        m=line.find(v)
        if m>-1 :
            i=i+1
        line = f.readline()
    f.close()
    i=bytes(i)
    content=""+mt+"清明节专题日访问PV为："+i
    title=""+mt+"清明节PV统计报表"
    writeStat(content)
    content=readStat()
    sendTextEmail("xingping.he@downjoy.com", title.encode("gbk"), content.encode("gbk"))
    sendTextEmail("yue.lu@downjoy.com", title.encode("gbk"), content.encode("gbk"))
    sendTextEmail("lin.he@downjoy.com", title.encode("gbk"), content.encode("gbk"))
def readStat():
    oldf=open(logPath+"/zt_stat.log")
    line = oldf.readline()           # 调用文件的 readline()方法
    content=""
    while line:
        content=content+line
        line = oldf.readline()
    oldf.close()
    return content
     
def writeStat(content):
     fp=open(logPath+"/zt_stat.log","a+");
     fp.write(content+'\n')
     fp.close()

if __name__ == '__main__':
    addPv()
#    raw_input("Press enter key to close")








