#!/usr/bin/python
# -*- #coding:cp936
#功能：定期清理服务器上已删除的文件(清理从后台删除时间超过30天的文件)

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
mailTo = ['liang.shan@downjoy.com', 'zhou.wu@downjoy.com']
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
PASSWD = "android.d.cn.cd.20130711"
handledate = str(datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d"))

conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
cursor = conn.cursor()

dunionPrefixArr=['http://qr.androidgame-store.com/new/game1/', 'http://down.androidgame-store.com/new/game1/', 'http://p.androidgame-store.com/new/game1/', 'http://u.androidgame-store.com/android/new/game1/']
#网宿推送，url不带“http://”
wangsuPrefixArr=['g.androidgame-store.com/android/new/game1/']

def notifyDunionCDN(postUrls):
    readCode=""
    global fp_dunion
    try:
        data={}
        data['username']='cdnpush'
        data['password']='cdn123!@#push'
        data['type']='1'
        data['url']=postUrls.replace("\r\n", "")
        data['decode']='n'
        url="http://pushwt.dnion.com/cdnUrlPush.do"
        aa=urllib.urlencode(data)
        socket.setdefaulttimeout(30) 
        fp_dunion=urllib.urlopen(url,aa)
        readCode=fp_dunion.read()
        print readCode
        fp_dunion.close()
        print "notice dnion cdn"
    except Exception,ex:
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
        print "+++++++++++++++++++++++++++++++++++++%s"%ex
    finally:
        if fp_dunion:
            fp_dunion.close()
        pass


def notifyWangsuCDN(postUrl):
    username='push'
    password='push123!@#'
    readCode=""
    global fp_wangsu
    try:
        param={}
        param['username']=username
        param['passwd']=md5hex("%s%s%s"%(username,password,postUrl))
        param['url']=postUrl
        url="http://wscp.lxdns.com:8080/wsCP/servlet/contReceiver"
        aa=urllib.urlencode(param)
        socket.setdefaulttimeout(30)
        fp_wangsu=urllib.urlopen(url,aa)
        readCode=fp_wangsu.read()
        print readCode
        fp_wangsu.close()
        print "notice wangsu cdn"
    except Exception,ex:
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
        print "=====================================%s"%ex
    finally:
        if fp_wangsu:
            fp_wangsu.close()
        pass

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

def getServerNodeInfos():
    sql="select ip,absolute_dir from SERVER_NODE where status=1 and need_sync=1 and copyright=%s"%(COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs = cursor.fetchall()
    i = 0
    for row in rs:
        ip = row[0]
        dir = row[1]
        serverNodeDict[ip] = dir

def deleteFile():
    pkgInfoPath="%sdelete_file_%s.txt"%(pkgInfoDir, handledate)
    fs = open(pkgInfoPath, 'wb')
    sql='''select H.URL, G.ID from GAME_PKG_HISTORY H inner join GAME G 
           on G.ID = H.GAME_ID 
           where datediff(now(), H.PUBLISH_DATE) >30  and datediff(now(), H.PUBLISH_DATE) <32
           and G.COPYRIGHT_TYPE =%s and H.URL not in(select url from GAME_PKG) '''%(COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs = cursor.fetchall()
    urlList = []
    for row in rs:
        if row and row[0]:
            urlList.append(row[0])
    cursor.close()
    conn.close()
    #需要推送的url
    NeedUpdateUrls = []
    for url in urlList:
        if url.find(DEFAULT_URL) < 0 :
            continue;
        NeedUpdateUrls.append(url.replace(DEFAULT_URL, ''))
        for serverNodeIp in serverNodeDict.keys():
            serverNodeDir = serverNodeDict[serverNodeIp]
            filePath = url.replace(DEFAULT_URL, serverNodeDir)
            md5 = md5hex("%s%s"%(filePath,PASSWD))
            requestUrl = "http://%s:10010/resopt/delete?path=%s&auth=%s"%(serverNodeIp, filePath,md5)
            fs.write(deleteRemoteFile(requestUrl))
        
        if len(NeedUpdateUrls)>20:
            notifyUrl_dnion = ""
            notifyUrl_wangsu = ""
            for url in NeedUpdateUrls:
                url = url.strip().lstrip().rstrip()
                for prefix in dunionPrefixArr:
                    notifyUrl_dnion = notifyUrl_dnion + "," + "%s%s"%(prefix,url)
                for prefix in wangsuPrefixArr:
                    notifyUrl_wangsu = notifyUrl_wangsu + ";" + "%s%s"%(prefix,url)
            notifyUrl_dnion = notifyUrl_dnion[1:]
            notifyDunionCDN(notifyUrl_dnion)
            notifyUrl_wangsu = notifyUrl_wangsu[1:]
            notifyWangsuCDN(notifyUrl_wangsu)
            NeedUpdateUrls = []
            time.sleep(600)
    fs.close()


def sendMail():
    global mailContents
    fileDateStr = datetime.datetime.strftime(fileDate, "%Y-%m-%d")
    mailContents = (mailContents + u'清理过期下载资源文件出错<br/>错误信息：%s<br/>'%(ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    

if __name__ == '__main__':
    print "=============start %s" % datetime.datetime.now()
    
    try:
        getServerNodeInfos()    
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
    print "=============end   %s" % datetime.datetime.now()



