#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: helin $"
__version__ = "$Revision: 1.9 $"
__date__ = "$Date: 2013/07/26 15:49:04 $"

import MySQLdb
import urllib
import smtplib
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import time
import datetime
import re
import hashlib

COPYRIGHT_TYPE = "0"
DEFAULT_URL="http://c.downandroid.com/android/new/emulatorgame/"
SERVERNODE_ARRAY = {}
MONITOR_MAIL=['shan.liang@downjoy.com','zhou.wu@downjoy.com']

conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
cursor = conn.cursor()

PASSWD = "41eacdf914ac456cabecf584e93f299c"

def getServerNodeInfos():
    sql="select ID,IP,ABSOLUTE_DIR from SERVER_NODE where COPYRIGHT=%s and NEED_SYNC=1 and STATUS = 1"%(COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs = cursor.fetchall()
    i = 0
    for row in rs:
	#print row
        id = row[0]
        ip = row[1]
        dir = row[2]
        SERVERNODE_ARRAY[i]=[id, ip, dir]
        i = i+1
        
def md5hex(word):
    """ MD5加密算法，返回32位小写16进制符号 """
    if isinstance(word, unicode):
        word = word.encode("utf-8")
    elif not isinstance(word, str):
        word = str(word)
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()


#如果文件大小为0则访问3次，减小网络造成返回文件大小错误的情况
def getFileSize(url):
    retryTime = 3
    fileSize = 0
    while retryTime > 0:
        fileSize = getFileSizeFromUrl(url)
        retryTime = retryTime - 1
        if fileSize > 0:
            return fileSize
    return fileSize
        
#获取远程服务器的文件大小
def getFileSizeFromUrl(url):
    fileSize="0"
    try:
        fp=urllib.urlopen(url)
        fileSize=fp.read()
        fp.close()
    finally:
        if str.isdigit(fileSize):
            return long(fileSize)
        else:
            return long(0)

def sendmail(From, To, msgBody, title):
    body = "服务器中文件大小与数据库的fileSize大小不一致:<br/><br/>%s"%(msgBody)
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","htbp3dQ1sGcco!q")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(body, 'html', 'gb2312')
    main_msg.attach(text_msg)

    main_msg['From'] = From
    main_msg['To'] = ', '.join(To)
    main_msg['Subject'] = title
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail(From, To, fullText)
    finally:
        server.quit()

#修改游戏状态
def changeSyncStatus():
    postUrls=""
    sql="select P.URL, P.FILE_SIZE, P.ID, P.EMULATOR_GAME_ID, P.CREATED_DATE from EMULATOR_GAME_PKG P inner join EMULATOR_GAME G on G.ID = P.EMULATOR_GAME_ID where P.SYNC_STATUS = 0 AND G.STATUS=1 order by P.ID ASC limit 20"
    cursor.execute(sql)
    rs1 = cursor.fetchall()  
    print len(rs1)
    msgBody=""
    for row1 in rs1:
        url=row1[0]
        pkgFileSize=long(row1[1])
        pkgId=row1[2]
        gId=row1[3]
        createdDate=time.strptime(str(row1[4]), "%Y-%m-%d %H:%M:%S")
        print "gameId:%s pkgId:%s"%(gId, pkgId)
        now=time.localtime()
        delayhours=(time.mktime(now)-time.mktime(createdDate))/3600
        
        #判断是否同步完成
        finishFlag = True
        for num in range(len(SERVERNODE_ARRAY)):
            serverNodeId = SERVERNODE_ARRAY[num][0]
            serverNodeIp = SERVERNODE_ARRAY[num][1]
            serverNodeDir = SERVERNODE_ARRAY[num][2]
            if serverNodeDir.find("e:")>-1 or serverNodeDir.find("d:")>-1 :
                filePath = url.replace(DEFAULT_URL, serverNodeDir).replace("/game1/", "/emulatorgame/").replace("/", "\\")
                requestUrl = "http://%s:11010/file.asp?path=%s"%(serverNodeIp, filePath)
                fileSize=getFileSize(requestUrl)
            else:
                filePath = url.replace(DEFAULT_URL, serverNodeDir).replace("/game1/", "/emulatorgame/")
                #http://58.215.241.59:10010/resopt/file?path=/usr/local/django/cdroid_py_cdn.zip&auth=d9facb576476280c1da68d5427a35d6a
                md5 = md5hex("%s%s"%(filePath,PASSWD))
                requestUrl = "http://%s:10010/resopt/file?path=%s&auth=%s"%(serverNodeIp, filePath,md5)
                fileSize=getFileSize(requestUrl)
                
            if pkgFileSize != fileSize:
                finishFlag = False
                break
        
        if finishFlag:
            sql="update EMULATOR_GAME_PKG set SYNC_STATUS = 1 where ID = %s and EMULATOR_GAME_ID = %s"%(pkgId, gId)
            print "pkgId:%s sync success"%(pkgId)
            cursor.execute(sql)
            conn.commit()    
        else:
            print "pkgId:%s sync not finished"%(pkgId)
            if delayhours >= 2:
                msgBody= msgBody + "EmulatorGameId:%s, pkgId:%s \n <br/>"%(gId,pkgId)
    if msgBody != "" :
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, msgBody, "模拟器游戏 同步文件出错,211.147.5.167_usr_local_bin_new_changeEmulatorGameSyncStatus.py") 
        
startTime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
print "new_changeEmulatorGameSyncStatus.py start at %s"%startTime

getServerNodeInfos()
changeSyncStatus()

#关闭连接
cursor.close()
conn.close()

endTime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
print "new_changeEmulatorGameSyncStatus.py end at %s"%endTime

