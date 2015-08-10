#!/usr/bin/python
# -*- #coding:cp936
import time
import datetime
import string
import os
import re
import smtplib
from email.Header import Header
from email.MIMEText import MIMEText

IMEI_ARRAY = [['',0] for x in range(50000)]
OS_ARRAY = [['',0] for x in range(20)]
RESOLUTION_ARRAY=[['',0] for x in range(100)]
IMEI_PATTERN = re.compile(r".*crtb=([^&]\w+).*")
OS_PATTERN = re.compile(r".*os=([^&]+).*")
RES_W_PATTERN = re.compile(r".*w=([^&]\d+).*")
RES_H_PATTERN = re.compile(r".*h=([^&]\d+).*")

logFileName = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days=1),"%y%m%d")
dlFileName = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days=1),"%Y-%m-%d")

def log(imei, os, w, h):
    global IMEI_ARRAY, OS_ARRAY, RESOLUTION_ARRAY
    for index in range(0,len(IMEI_ARRAY)):
        if IMEI_ARRAY[index][0] == imei:
            IMEI_ARRAY[index][1] = IMEI_ARRAY[index][1] + 1
            break
        elif IMEI_ARRAY[index][0] == "":
            IMEI_ARRAY[index][0] = imei
            IMEI_ARRAY[index][1] = 1
            break

    for index in range(0,len(OS_ARRAY)):
        if OS_ARRAY[index][0] == os:
            OS_ARRAY[index][1] = OS_ARRAY[index][1] + 1
            break
        elif OS_ARRAY[index][0] == "":
            OS_ARRAY[index][0] = os
            OS_ARRAY[index][1] = 1
            break

    res = w + "*" + h
    for index in range(0,len(RESOLUTION_ARRAY)):
        if RESOLUTION_ARRAY[index][0] == res:
            RESOLUTION_ARRAY[index][1] = RESOLUTION_ARRAY[index][1] + 1
            break
        elif RESOLUTION_ARRAY[index][0] == "":
            RESOLUTION_ARRAY[index][0] = res
            RESOLUTION_ARRAY[index][1] = 1
            break      
    
            

def loopLine():
    global IMEI_PATTERN,OS_PATTERN,RES_W_PATTERN,RES_H_PATTERN
    
    #f = open("C:\\Users\\y\\Desktop\\androiddcn_ex100706.log")
    f = open("/usr/local/apache/logs/accesslog/androiddcn_ex"+logFileName+".log")
    while True:
        line = f.readline()
        if line == None or len(line) == 0 :
            break
        if line.find("GET /xml/")>0:
            imei = os = w = h = None
            if IMEI_PATTERN.match(line):
                imei = IMEI_PATTERN.match(line).group(1)
            if OS_PATTERN.match(line):
                os = OS_PATTERN.match(line).group(1)
            if RES_W_PATTERN.match(line) and RES_H_PATTERN.match(line):
                w = RES_W_PATTERN.match(line).group(1)
                h = RES_H_PATTERN.match(line).group(1)
            if imei!=None and len(imei) > 0 and os!=None and len(os) > 0 and w!=None and len(w) > 0 and h!=None and len(h) > 0:
                log(imei,os,w,h)
    f.close()
                

def report():
    ret="PV部分：\n-----------------------\n独立用户数\t"
    count=0
    global IMEI_ARRAY, OS_ARRAY, RESOLUTION_ARRAY
    
    for index in range(0,len(IMEI_ARRAY)):
        if IMEI_ARRAY[index][0]=="":
            break
        else:
            count = count + 1
    ret = ret + str(count) + "\n\n操作系统分布:\n"
    
    for index in range(0,len(OS_ARRAY)):
        if OS_ARRAY[index][0]=="":
            break
        else:
            ret = ret + OS_ARRAY[index][0] +"\t"+ str(OS_ARRAY[index][1]) + "\n"
    
    ret = ret + "\n分辨率分布:\n"   
    for index in range(0,len(RESOLUTION_ARRAY)):
        if RESOLUTION_ARRAY[index][0]=="":
            break
        else:
            ret = ret + RESOLUTION_ARRAY[index][0] +"\t"+ str(RESOLUTION_ARRAY[index][1]) + "\n"
    
    ret=ret+"下载量：\n--------------------------\n"+str(getDownloadLogLines())+"\n"
    
    return ret

def getDownloadLogLines():
    count = 0
    f = open("/home/downjoy/w3clog/digua."+dlFileName+".txt","r")
    while True:
        line = f.readline()
        if len(line)==0:
            break
        else:
            count = count+1
    return count
   
def sendMail():
    mailto_list = ["jacky@downjoy.com","gao.ge@downjoy.com","dust@downjoy.com","chao.nie@downjoy.com"]
    mail_host = "mail.downjoy.com"
    mail_user = "webmaster@downjoy.com"
    mail_pass = "htbp3dQ1sGcco!q"
    mail_from = "当乐数据中心<webmaster@downjoy.com>"
    mail_postfix = "downjoy.com"
    body = "地瓜游戏数据统计\n"
    body = body + report()
    body = body + "本邮件为自动信，如果遇到任何问题请向Miles反馈，谢谢！"
    mail_subject = "地瓜游戏数据日报 " + dlFileName+ "PV及下载量"
    me = mail_from+"<"+mail_user+">"
    #print body
    msg = MIMEText(body,_subtype='plain',_charset='gb2312')
    msg['Subject'] = mail_subject
    msg['From'] = mail_from
    msg['To'] = ";".join(mailto_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(me, mailto_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

    
def main():
    loopLine()
    sendMail()

main()    
