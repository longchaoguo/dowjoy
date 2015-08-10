#!/usr/bin/python
# -*- coding: utf-8 -*-

#Created on 2011-11-25
#@author: li.dai
import os.path
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import datetime as dt
import time
import MySQLdb
from xlrd import open_workbook
from xlutils.copy import copy
import xlwt
from xlwt import Formula
import sys
reload(sys)
sys.setdefaultencoding("utf8")

def openDroidGameConn():
    try:
        DroidGameConn = MySQLdb.connect(host='192.168.0.16', user='moster', passwd='shzygjrmdwg', db='droid_game', port=3306, charset="utf8", use_unicode="True")
        return DroidGameConn
    except Exception,e:
        print str(e);
        #sys.exit();

def closeConn(conn):
    conn.close();

def getRs(conn, sql):
    try:
        cursor = conn.cursor();
        cursor.execute(sql);
        rows = cursor.fetchall();
        conn.commit();
        return rows;
    except:
        pass;
    finally:
        try:
            cursor.close();
        except:
            pass;

def execSql(conn, sql):
    try:
        cursor = conn.cursor();
        cursor.execute(sql.decode("gb2312"));
        conn.commit();
        print sql
    except:
        pass;
        print sql
    finally:
        try:
            cursor.close();
        except:
            pass;

def getOlineUser(DroidGameConn):
    onlineUserRows = getRs(DroidGameConn, ("select IMEI, VERSION_CODE from CLIENT_STAT_ONLINE_USER order by VERSION_CODE"))
    return onlineUserRows

def SendMail(mail_to, mail_subject, mail_body, filepath, filename):
    mail_host = "mail.downjoy.com"
    mail_user = "webmaster@downjoy.com"
    mail_pass = "htbp3dQ1sGcco!q"
    mail_from = u"当乐数据中心<webmaster@downjoy.com>"

    msg = MIMEMultipart()
    body = MIMEText(mail_body,_subtype='plain',_charset='gb2312')
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
            s.login(mail_user,mail_pass)
            s.sendmail(mail_from, mail_to, msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            pass

def sendMail():
    lastDate = dt.date.today() - dt.timedelta(days=1)
    mail_to = ["baiwei.zhan@downjoy.com"]
    mail_subject = u"地瓜在线用户版本分布统计"
    mail_body = u"您好！\n    %s日的地瓜在线用户版本分布统计表，详见附件，谢谢。"%lastDate
    filepath =''
    filename = "digua_online_user_version_" + str(lastDate) + ".xls"
    
    SendMail(mail_to, mail_subject, mail_body.encode('gb2312'), filepath, filename)
    
    if os.path.exists(filepath+filename):
        os.remove(filepath+filename)

def saveExcel(path, versionAndUsers):
    try:
        #第一次运行或0点运行，新建一个excel文件
        if not os.path.exists(path):
            sendMail()
            wb = xlwt.Workbook()
            sheet = wb.add_sheet("sheet 1")
            sheet.write(0, 0, u"版本号")
            sheet.write(0, 1, u"平均人数")
            sheet.write(0, 2, u"百分比")
            i = 1
            for (k, v) in sorted(versionAndUsers.items(), key=lambda d:d[0]):
                sheet.write(i, 0, k);
                sheet.write(i, 1, v);
                i += 1
            style = xlwt.easyxf(num_format_str='0.00%')
            for rownum in range(1, i):
                sheet.write(rownum, 2, Formula("B%d/SUM(B2:B%d)"%(rownum+1, i)), style)
            wb.save(path)
        else:
            rb = open_workbook(path)
            rs = rb.sheet_by_index(0)
            wb = copy(rb)
            ws = wb.get_sheet(0)
            for rownum in range(1, rs.nrows):
                diguaVersion = rs.cell(rownum, 0).value
                users = rs.cell(rownum, 1).value
                if not versionAndUsers.has_key(diguaVersion):
                    versionAndUsers[diguaVersion] = int(users/2)
                else:
                    versionAndUsers[diguaVersion] = int((versionAndUsers[diguaVersion] + users)/2)
            i = 1
            for (k, v) in sorted(versionAndUsers.items(), key=lambda d:d[0]):
                ws.write(i, 0, k);
                ws.write(i, 1, v);
                i += 1
            style = xlwt.easyxf(num_format_str='0.00%')
            for rownum in range(1, i):
                ws.write(rownum, 2, Formula("B%d/SUM(B2:B%d)"%(rownum+1, i)), style)
            wb.save(path)
    except:
        for inf in sys.exc_info():
            print inf

def main():
    start = time.time()
    print("#########start =>")
    versionAndUsers = {}
    DroidGameConn = openDroidGameConn()
    onlineUserRows = getOlineUser(DroidGameConn)
    #onlineUserRows = [('A1000009EC3091', 232), ('355430041532664', 231), ('A100001B3A8453', 24), ('A100001B3A8453', 37), ('A100001B3A8453', 23), ('A100001B3A8453', 24), ('A100001B3A8453', 36), ('A100001B3A8453', 35),('A100001B3A8453',22),('A100001B3A8453',20),('A100001B3A8453', 30),('A100001B3A8453', 37),('A100001B3A8453', 37),('A100001B3A8453', 37),('A100001B3A8453', 37),('A100001B3A8453', 38),('A100001B3A8453', 38)]
    for user in onlineUserRows:
        diguaVersion = str(user[1])[0:2]
        if not versionAndUsers.has_key(diguaVersion):
            versionAndUsers[diguaVersion] = 1
        else:
            versionAndUsers[diguaVersion] += 1
    path = "digua_online_user_version_" + time.strftime('%Y-%m-%d',time.localtime(time.time())) + ".xls"
    saveExcel(path, versionAndUsers)
    
    closeConn(DroidGameConn)
    print("#########over. use %s")%(time.time()-start)

main()
