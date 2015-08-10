#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: liangshan$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2014/10/20 17:46 $"

#####################################################
#此脚本每天执行一次，将安卓总下载量top300更新至旧top300表里。
#####################################################
import datetime
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.ScriptExecuteUtil import ScriptExecuteUtil

handleDay = datetime.datetime.today() - datetime.timedelta(1)
handledate = str(datetime.datetime.strftime(handleDay, "%Y-%m-%d"))
dbUtil_droid_game=DBUtil('droid_game_10')
dbUtil_download_stat=DBUtil('download_stat_168')

#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"当乐数据中心".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"安卓总下载量统计错误信息".encode("gbk")
mailTo=['shan.liang@downjoy.com']
mailContents=u'Hi: \n'

#每天将过去总下载量top300更新至旧top300表里
def updateTotalData(type):
    table = ""
    if type == 1:#游戏
        table = "DOWNLOAD_TOTAL_GAME_TOP300"
    else:
        return
        
    #删除旧数据
    sql = "delete from %s" %(table)
    dbUtil_droid_game.delete(sql)
    
    #查询新的总下载量排行
    sql = "select GAME_ID, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where GAME_ID>0 and RESOURCE_TYPE=%s group by GAME_ID order by CNT desc limit 300"
    rows = dbUtil_download_stat.queryList(sql, (type))
    if not rows:
        return
    for row in rows:
        vendorId = getVendorIdByGameId(row[0])
        #排除一些特定厂商的游戏
        if vendorId != 0 and vendorId != 9 and vendorId != 49:
            sql = "insert into %s (GAME_ID, CNT, STAT_DATE) values(%s, %s, '%s')" % (table, row[0], row[1], handledate)
            dbUtil_droid_game.insert(sql)

#查询厂商ID       
def getVendorIdByGameId(gameId):
    sql="select VENDOR_ID from GAME where ID = %s"
    rs = dbUtil_droid_game.queryRow(sql, (gameId))
    try:
        vendorId=rs[0]
    except:
        vendorId=0
    return vendorId

#邮件
def sendMail():
    global mailContents
    mailContents=(mailContents+u'总下载量统计脚本执行出错，\n错误信息：%s\n谢谢'%(ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
if __name__ == "__main__":
    print "=============start %s===="%datetime.datetime.now()
    try:
        #更新游戏总排行列表
        updateTotalData(1)
    except Exception, ex:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if dbUtil_droid_game: dbUtil_droid_game.close()
        if dbUtil_download_stat: dbUtil_download_stat.close()
        if ERROR_MSG:
            sendMail()
    print "=============end   %s===="%datetime.datetime.now()