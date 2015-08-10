#!/usr/bin/python
#-*-#coding: cp936

__author__="$Author: xin.wen$"
__version__="$Version: 1.0$"
__date__="$Date: 2012-11-13 23:17:00$"

import datetime
import xlwt
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil

yesterday=datetime.datetime.strftime(datetime.datetime.today()-datetime.timedelta(days=1),'%Y-%m-%d')
#yesterday='2013-11-24'
nextDay=datetime.datetime.strftime(datetime.datetime.strptime(yesterday,'%Y-%m-%d')+datetime.timedelta(days=1), '%Y-%m-%d')
lastDay=datetime.datetime.strftime(datetime.datetime.strptime(yesterday,'%Y-%m-%d')-datetime.timedelta(days=1), '%Y-%m-%d')

GAME_DICT={}
CHANNEL_FLAG_NAME_DICT={10:u'web', 20:'wap', 30:u'�ع�', 70:u'�㶹��һ����װ', 60:u'�㶹�Ժ���', 50:u'360һ����װ', 40:u'360����', 80:u'�ٶ�', 90:u'��Ѷ����', 100:u'��Ѷһ����װ', 110:'��Ѷר��', 120:u'���غ���', 130:u'360�ۺ�'}
CHANNEL_FLAG_DICT={10:{1:[],2:[]}, 20:{1:[],2:[]}, 30:{1:[],2:[]}, 40:{1:[],2:[]}, 50:{1:[],2:[]}, 60:{1:[],2:[]}, 70:{1:[],2:[]}, 80:{1:[],2:[]}, 90:{1:[],2:[]}, 100:{1:[],2:[]}, 110:{1:[],2:[]}, 120:{1:[],2:[]}, 130:{1:[],2:[]}, 140:{1:[],2:[]}}
dbUtil=DBUtil("droid_game_10")
dbUtil_168=DBUtil('download_stat_168')

filePath='/usr/local/bin/cdroid/report/data/'
fileName=filePath+'android_top100_for_channel_flag_%s.xls'%lastDay
###��������
mailServer = "mail.downjoy.com"
mailFromName=u"������������".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailTo = ['lin.he@downjoy.com', 'christina.gu@downjoy.com', 'dong.wei@downjoy.com', 'jacky@downjoy.com','chengbao.yang@downjoy.com','leepong@downjoy.com','xinjie.wang@downjoy.com']
#mailTo = ['qicheng.meng@downjoy.com']
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = (u"Android�������������ձ���TOP100_%s"%(lastDay)).encode("gbk") #�ʼ�����
mailContents = (u"Hi,����%s��Android������������TOP100ͳ�Ʊ������쳣������������ϵ��лл"%(lastDay)).encode("gbk")
###############################
def getGameData():
    sql="select ID, NAME from GAME"
    rows=dbUtil.queryList(sql, ())
    for row in rows:
        GAME_DICT[int(row[0])]=row[1].decode('utf-8')

def getDownData():
    sql="select CHANNEL_FLAG, GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where CREATED_DATE>='%s' and CREATED_DATE<'%s' group by CHANNEL_FLAG, GAME_ID, RESOURCE_TYPE order by CHANNEL_FLAG, RESOURCE_TYPE, CNT desc"%(lastDay, yesterday)
    #print sql
    rows=dbUtil_168.queryList(sql, ())
    for row in rows:
        channelFlag=int(row[0])
        gameId=int(row[1])
        type=int(row[2])
        downs=int(row[3])
        tempList=CHANNEL_FLAG_DICT.get(channelFlag,{}).get(type)
        if tempList==None : continue
        tempList.append([gameId, downs])

def writeFile():
    book=xlwt.Workbook(encoding='gbk', style_compression=True)
    keys=CHANNEL_FLAG_NAME_DICT.keys()
    keys.sort()
    for key in keys:
        sheet=book.add_sheet(CHANNEL_FLAG_NAME_DICT.get(key), cell_overwrite_ok=True)
        tempDict=CHANNEL_FLAG_DICT.get(key)
        sheet.write(0,0,u'��Ϸ'.encode('gbk'))
        sheet.write(0,1,u'ͳ�����ڣ�%s'%(lastDay))
        sheet.write(0,4,u'���'.encode('gbk'))
        for k,v in tempDict.items():
            x=0
            y=2
            if k==2: x=4
            sheet.write(1,x, u'ID')
            sheet.write(1,x+1, u'����'.encode('gbk'))
            sheet.write(1,x+2, u'������'.encode('gbk'))
            for tempList in v:
                sheet.write(y, x, tempList[0])
                sheet.write(y, x+1, GAME_DICT.get(tempList[0]))
                sheet.write(y, x+2, tempList[1])
                y=y+1
                if y>102:
                    break
    book.save(fileName)

def sendMail():
    mail=MailUtil(fileName, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailAttachment(mailContents)
    
if __name__=='__main__':
    getGameData()
    getDownData()
    writeFile()
    sendMail()
    dbUtil.close()
    dbUtil_168.close()
        
        
    
    
    
