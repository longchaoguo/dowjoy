#!/usr/bin/python
# -*- #coding:cp936
#功能：定期清理资源上传服务器上过期的文件
import MySQLdb
import urllib
import datetime
import re
import urllib
import urllib2
import time
import hashlib
import StringIO
import traceback
import socket

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"资源清理".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
now = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d")
mailSubject = u"清理过期下载资源文件出错%s"%(now).encode("gbk")
mailTo = ['liang.shan@downjoy.com', 'lin.he@downjoy.com']
mailContents = u'Hi: <br/>'
###########################################################

#是否为版权游戏
COPYRIGHT_TYPE = "0"
#删除文件记录路径
pkgInfoDir="/home/downjoy/game_pkg_info/"
#数据库中默认的存储文件路径
DEFAULT_URL="http://c.downandroid.com/android/new/game1/"
#存放有效的要删除文件的服务器的信息
serverNodeDict = {}
PASSWD = "41eacdf914ac456cabecf584e93f299c"
handledate = str(datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d"))

conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
cursor = conn.cursor()


def md5hex(word):
    """ MD5加密算法，返回32位小写16进制符号 """
    if isinstance(word, unicode):
        word = word.encode("utf-8")
    elif not isinstance(word, str):
        word = str(word)
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()



def deleteRemoteFile(url):
    msg=""
    try:
        global fp
        fp=urllib.urlopen(url)
        msg=fp.read()
    except Exception, ex:
        print "xxxxx"
    finally:
        fp.close()
        print "%s|%s"%(url, msg)
        return "%s|%s\n"%(url, msg)


def deleteFile():
    pkgInfoPath="%sdelete_uploadserver_file_%s.txt"%(pkgInfoDir, handledate)
    fs = open(pkgInfoPath, 'wb')
    sql='''select H.URL from GAME_PKG_HISTORY H inner join GAME G 
           on G.ID = H.GAME_ID 
           where datediff(now(), H.PUBLISH_DATE) < 2
           AND G.COPYRIGHT_TYPE =%s
           union all
           select P.URL from GAME_PKG P inner join GAME G 
           on G.ID = P.GAME_ID 
           where datediff(now(), P.CREATED_DATE) > 2 
           AND datediff(now(), P.CREATED_DATE) < 4 
           AND G.COPYRIGHT_TYPE =%s AND P.SYNC_STATUS=1 '''%(COPYRIGHT_TYPE,COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs = cursor.fetchall()
    urlList = []
    for row in rs:
        if row and row[0]:
            urlList.append(row[0])
    cursor.close()
    conn.close()
    #需要推送的url
    for url in urlList:
        if url.find(DEFAULT_URL) < 0 :
            continue;
        for serverNodeIp in serverNodeDict.keys():
            serverNodeDir = serverNodeDict[serverNodeIp]
            filePath = url.replace(DEFAULT_URL, serverNodeDir)
            md5 = md5hex("%s%s"%(filePath,PASSWD))
            requestUrl = "http://%s:10010/resopt/delete?path=%s&auth=%s"%(serverNodeIp, filePath,md5)
            fs.write(deleteRemoteFile(requestUrl))
        
    fs.close()


def sendMail():
    global mailContents
    fileDateStr = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
    mailContents = (mailContents + u'清理过期下载资源文件出错<br/>错误信息：%s<br/>'%(ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    

if __name__ == '__main__':
    print "deleteUploadServerNodesFiles.py=============start %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
    
    try:
        serverNodeDict["115.182.49.210"] = "/usr/local/data_resource/android/new/game1/"
        #serverNodeDict["115.182.49.211"] = "/usr/local/data_resource/android/new/game1/"
        deleteFile()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if cursor: 
            cursor.close()
        if cursor.close():
            conn.close()
        if ERROR_MSG:
            print ERROR_MSG
            sendMail(fileDate)
    print "deleteUploadServerNodesFiles.py=============end %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))



