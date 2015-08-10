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
CHANNEL_FLAG_NAME_DICT={10:u'web', 20:'wap', 30:u'地瓜', 70:u'豌豆荚一键安装', 60:u'豌豆荚合作', 50:u'360一键安装', 40:u'360合作', 80:u'百度', 90:u'腾讯搜索', 100:u'腾讯一键安装', 110:'腾讯专区', 120:u'多特合作', 130:u'360聚合'}
CHANNEL_FLAG_DICT={10:{1:[],2:[]}, 20:{1:[],2:[]}, 30:{1:[],2:[]}, 40:{1:[],2:[]}, 50:{1:[],2:[]}, 60:{1:[],2:[]}, 70:{1:[],2:[]}, 80:{1:[],2:[]}, 90:{1:[],2:[]}, 100:{1:[],2:[]}, 110:{1:[],2:[]}, 120:{1:[],2:[]}, 130:{1:[],2:[]}, 140:{1:[],2:[]}}
dbUtil=DBUtil("droid_game_10")
dbUtil_168=DBUtil('download_stat_168')

filePath='/usr/local/bin/cdroid/report/data/'
fileName=filePath+'android_top100_for_channel_flag_%s.xls'%lastDay
###邮箱配置
mailServer = "mail.downjoy.com"
mailFromName=u"当乐数据中心".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailTo = ['lin.he@downjoy.com', 'christina.gu@downjoy.com', 'dong.wei@downjoy.com', 'jacky@downjoy.com','chengbao.yang@downjoy.com','leepong@downjoy.com','xinjie.wang@downjoy.com']
#mailTo = ['qicheng.meng@downjoy.com']
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = (u"Android下载量分渠道日报表TOP100_%s"%(lastDay)).encode("gbk") #邮件主题
mailContents = (u"Hi,这是%s日Android下载量各渠道TOP100统计表。若有异常请与蒙启成联系。谢谢"%(lastDay)).encode("gbk")
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
        sheet.write(0,0,u'游戏'.encode('gbk'))
        sheet.write(0,1,u'统计日期：%s'%(lastDay))
        sheet.write(0,4,u'软件'.encode('gbk'))
        for k,v in tempDict.items():
            x=0
            y=2
            if k==2: x=4
            sheet.write(1,x, u'ID')
            sheet.write(1,x+1, u'名称'.encode('gbk'))
            sheet.write(1,x+2, u'下载量'.encode('gbk'))
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
        
        
    
    
    
