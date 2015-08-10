#!/usr/bin/python
# -*- coding: cp936 -*-

import os
import time
import urllib
import urllib2
import re
import time
import datetime
import smtplib
import mimetypes
import random
import MySQLdb
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
import httplib

dbUtil_10 = DBUtil('droid_game_10')

mailToUsers = ["guoqiang.sun@downjoy.com"]

#ʹ�ô������ 
def getHtmlContent(url): 
  req = urllib2.Request(url)
  res_data = urllib2.urlopen(req)
  res = res_data.read()
  return res

'''def getHtmlContent(url) :
  time.sleep(random.randint(10, 30))
  proxy_support = urllib2.ProxyHandler({'http':'211.142.236.135:80'})  
  opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)  
  urllib2.install_opener(opener)
  content = urllib2.urlopen(url).read()'''

def getChannelInfo():
  sql = "SELECT G.CHANNEL_ID,P.URL FROM NETGAME_GAME G INNER JOIN NETGAME_GAME_PKG P ON (G.ID=P.GAME_ID) WHERE G.STATUS=1 AND P.`NETGAME_SYNC_STATUS`=1 AND P.URL IS NOT NULL AND DATE_ADD(P.CREATED_DATE, INTERVAL '30:0' MINUTE_SECOND)>NOW()"
  return dbUtil_10.queryList(sql, ())


def getCachePkgUrl(cid):
    url="http://api.digua.d.cn/misc/ngchannel/url?id="+str(cid)
    content = getHtmlContent(url)
    return content

def cleanCache(ids):
    url='http://api.digua.d.cn/clean/ng/detail?ids='+ids
    getHtmlContent(url)

def sendMail(newIds):
    ERROR_MSG=None
    mailServer = "mail.downjoy.com"
    mailFromName=u"������������".encode("gbk")
    mailFromAddr="webmaster@downjoy.com"
    mailLoginUser = "webmaster@downjoy.com"
    mailLoginPass = "htbp3dQ1sGcco!q"
    mailSubject=u"���ֶ�������������ChannelId".encode("gbk")
    mailTo=['qicheng.meng@downjoy.com']
    mailContents=(u'Hi: \n���ֶ������������ݣ�channelIdΪ��%s\nлл��'%(str(newIds))).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

def getChannelIds():
    channelInfo=getChannelInfo()
    newIds=""
    for channel in channelInfo:
        cachaUrl=getCachePkgUrl(channel[0])
        #print channel[1]
        if cachaUrl!=channel[1]:
            newIds=newIds+str(channel[0])+','
    return newIds[0:len(newIds)-1]

def main():
    newIds=getChannelIds()
    print newIds
    if len(newIds)>0:
        cleanCache(newIds[0:len(newIds)-1])
    time.sleep(300)
    newIds=getChannelIds()
    if len(newIds)>0:
        sendMail(newIds)
    dbUtil_10.close()
    
main()
