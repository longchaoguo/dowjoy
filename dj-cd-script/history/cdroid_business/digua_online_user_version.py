#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#@author: daiyichuan
#
#统计地瓜在线用户数
#部署服务器：192.168.0.168
#部署路径:/usr/local/bin/cdroid_business
#脚本执行时间：每小时执行一次
#
# 

import os.path
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import datetime as dt
import time
from xlrd import open_workbook
from xlutils.copy import copy #@UnresolvedImport
import xlwt
from xlwt import Formula
import sys
import re
import urllib2
reload(sys)
sys.setdefaultencoding("utf8")

def SendMail(mail_to, mail_subject, mail_body, filepath, filename):
    mail_host = "mail.downjoy.com"
    mail_user = "webmaster@downjoy.com"
    mail_pass = "htbp3dQ1sGcco!q"
    mail_from = u"当乐数据中心<webmaster@downjoy.com>"

    msg = MIMEMultipart()
    body = MIMEText(mail_body, _subtype='plain', _charset='gb2312')
    if not os.path.exists(filepath + filename):
        print "do not send mail in first time"
    else:
        attachment = MIMEText(open(filepath + filename, 'rb').read(), 'base64', 'gb2312')
        attachment["Content-Type"] = 'application/octet-stream'
        attachment["Content-Disposition"] = "attachment; filename=" + filename
        msg.attach(attachment)
    
        msg.attach(body)
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = ";".join(mail_to)
        
        try:
            s = smtplib.SMTP()
            s.connect(mail_host)
            s.login(mail_user, mail_pass)
            s.sendmail(mail_from, mail_to, msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            pass

def sendMail(filePath, filePathName):
    lastDate = dt.date.today() - dt.timedelta(days=1)
    mail_to = ["zhou.wu@downjoy.com", "shan.liang@downjoy.com", "weii.liu@downjoy.com"]
    mail_subject = u"地瓜在线用户统计"
    mail_body = u"您好！\n    %s日的地瓜在线用户统计表，详见附件，谢谢。" % lastDate
    SendMail(mail_to, mail_subject, mail_body.encode('gb2312'), filePath, filePathName)


def saveExcel(path, fileName, onlineUser):
    excelPath = path + fileName;
    hour = int(time.strftime('%H',time.localtime(time.time())));
    try:
        if not os.path.exists(excelPath):
            wb = xlwt.Workbook()
            sheet = wb.add_sheet("sheet 1")
            sheet.write(0, 0, "date")
            for i in range(0,24):
                sheet.write(0, i+1, "%s:00"%(i))
            
            sheet.write(1, 0, time.strftime('%Y-%m-%d',time.localtime(time.time())));
            sheet.write(1, hour+1, onlineUser);
            wb.save(excelPath)
        else:
            rb = open_workbook(excelPath)
            rs = rb.sheet_by_index(0)
            wb = copy(rb)
            ws = wb.get_sheet(0)
            #列数
            y = rs.nrows-1
            
            if len(str(rs.cell(y, hour+1).value)) is 0:
                ws.write(y, hour+1, onlineUser);
                wb.save(excelPath) 
            if not len(str(rs.cell(y,24).value)) is 0:  
                sendMail(path, fileName);
                ws.write(y+1, 0, time.strftime('%Y-%m-%d',time.localtime(time.time())));
                ws.write(y+1, 1, onlineUser);
                wb.save(excelPath) 
            
            
    except Exception, e:
            print str(e)
            pass
    
def getOlineUser(jsonDoc):
    try:
        reg = r'\"IMEI\":"(.*?)"'
        result = re.findall(reg, jsonDoc)   
    except Exception, e:
        print str(e)
        pass
    return result

def getDoc(url):
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        print url
        return None    
    return html

def main():
    # 新地瓜服务（6.9版本以上游戏中心，含6.9）
    path = "/home/downjoy/logs/cdroid_business/"
    pathFileName = "newdigua_onLine_user.xls"
    url_a = "http://192.168.0.222:7041/newdiguaserver/onlineUser"
    url_b = "http://192.168.0.236:7041/newdiguaserver/onlineUser"
    url_c = "http://192.168.0.237:7041/newdiguaserver/onlineUser"
    url_d = "http://192.168.0.238:7041/newdiguaserver/onlineUser"
    url_e = "http://192.168.0.239:7041/newdiguaserver/onlineUser"
    array = getOlineUser(getDoc(url_a)) + getOlineUser(getDoc(url_b)) + getOlineUser(getDoc(url_c)) + getOlineUser(getDoc(url_d)) + getOlineUser(getDoc(url_e))
    onLine_user = len(set(array))
    saveExcel(path, pathFileName, onLine_user)

    # 老地瓜服务（6.9版本以前游戏中心，不含6.9）
    pathFileName = "olddigua_onLine_user.xls"
    url_a = "http://192.168.0.222:7011/onlineUser"
    url_b = "http://192.168.0.236:7011/onlineUser"
    url_c = "http://192.168.0.237:7011/onlineUser"
    url_d = "http://192.168.0.238:7011/onlineUser"
    url_e = "http://192.168.0.239:7011/onlineUser"
    array = getOlineUser(getDoc(url_a)) + getOlineUser(getDoc(url_b)) + getOlineUser(getDoc(url_c)) + getOlineUser(getDoc(url_d)) + getOlineUser(getDoc(url_e))
    onLine_user = len(set(array))
    saveExcel(path, pathFileName, onLine_user)

main()
