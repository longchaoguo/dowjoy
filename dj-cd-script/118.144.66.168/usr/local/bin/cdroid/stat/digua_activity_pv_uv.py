#!/usr/bin/python
#-*-#coding: utf8

__author__ = "$Author: shan.liang $"
__version__ = "$Vision: 1.0 $"
__date__ = "$Date: 2014/9/12 17:00:00 $"

import re
import sys
import datetime
import StringIO
import traceback
import os
from djutil.OptsUtil import OptsUtil
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil

##################################################
#地瓜专题PV(用户浏览量)、UV(用户访问量)信息统计
##################################################
handleDay=None
droid_stat_until=DBUtil('droid_stat_168')
droid_game_until=DBUtil('droid_game_10')
pattern=re.compile("\[(?P<TIME>\S* \S*)\] (?P<SERIAL>\S*)\|(?P<ID>\S*)")
ACTIVITY_PV_DICT={}

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"地瓜专题日志统计错误信息".encode("gbk")
mailTo = ['guoqiang.sun@downjoy.com']
mailContents = u'Hi: \n'

#初始化时间
def init():
    global handleDay
    opts=OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate=datetime.datetime.strftime(datetime.datetime.today()-datetime.timedelta(days=1), "%Y-%m-%d")
    else:
        fileDate=opts.get('--FILE_DATE')
    print fileDate
    handleDay = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")

#清除临时表中的数据
def clearData():
    sql = "delete from DIGUA_ACTIVITY_PV_UV where datediff(%s,TIME) = 0"
    droid_stat_until.delete(sql, (handleDay))
    sql = "truncate DIGUA_ACTIVITY_VISIT_INFO_TEMP"
    droid_stat_until.truncate(sql, ())

#插入数据
def insertData(dbUtil, sql, dataList):
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass
                
#获取日志文件路径
def getLogPath():
    sql="select LOCAL_DIR, LOCAL_FILE from FTP_LOG_CONFIG where id in (177,178,179,180,209,229) order by ID;"
    rows = droid_stat_until.queryList(sql, ())
    for row in rows:
        if not row:
            continue
        analyzeLog(row[0], row[1]%(handleDay))

#分析日志文件信息，插入临时表
def analyzeLog(dir,fileName,flag = 'False'):
    sql='insert into DIGUA_ACTIVITY_VISIT_INFO_TEMP(ACTIVITY_ID, SERIAL) values(%s, %s)'
    dataList = []
    logPath = dir+fileName;
        # 如果该文件不存在，抛出异常
    if os.path.exists(logPath):
        f=open(logPath, "rb")
        while True:
            line=f.readline()
            if not line:
                break
            line=line.strip()
            m=pattern.match(line)
            if not m:
                continue
            serial=m.group('SERIAL')
            id=m.group('ID')
            dataList.append((id, serial))
            if len(dataList) >= 1000:
                    insertData(droid_stat_until, sql, dataList)
                    dataList = []
        if dataList:
            insertData(droid_stat_until, sql, dataList)
            dataList = []
        f.close()
        if(str(flag) == 'True'):
            os.remove(dir+fileName)
    else:
        if(str(flag) == 'True'):
            ERROR_MSG = u'解压文件%sbak/%s.tar.gz失败' %(dir,fileName)
            sendMail()
            return
        cmd = "tar -xzvf  %sbak/%s.tar.gz -C %s" %(dir,fileName,dir)
        print cmd
        os.system(cmd)
        flag = 'True'
        analyzeLog(dir,fileName,flag)

#统计PV、UV，并入库
def countPvAndUv():
    countSql='SELECT T.ACTIVITY_ID, COUNT(T.SERIAL), COUNT(DISTINCT(T.SERIAL)) FROM DIGUA_ACTIVITY_VISIT_INFO_TEMP T GROUP BY T.ACTIVITY_ID'
    insertSql='insert into DIGUA_ACTIVITY_PV_UV(ACTIVITY_ID, PV, UV, TIME) values (%s, %s, %s, "' + handleDay  + '")'
    print insertSql
    startIdx = 0
    pageNum = 1000
    while True:
        curSql = countSql + ' limit %s, %s'
        rows = droid_stat_until.queryList(curSql, ((startIdx, pageNum)))
        if not rows:
            break
        else:
            insertData(droid_stat_until, insertSql, rows)
            startIdx += pageNum
'''
 更新地瓜库的activity表的view表字段值
'''
def updateActivityView():
    resultSql = "SELECT ACTIVITY_ID,SUM(PV) FROM DIGUA_ACTIVITY_PV_UV WHERE TIME<='%s' GROUP BY  ACTIVITY_ID" %(handleDay)
    updateSql = 'UPDATE ACTIVITY SET VIEWS=%s where id=%s'
    results = droid_stat_until.queryList(resultSql,())
    dataList = []
    if not results and len(results)<1:
        return
    for result in results:
        dataList.append((result[1],result[0]))
    try:
        droid_game_until.insertMany(updateSql,dataList)
    except Exception,e:
        global ERROR_MSG
        ERROR_MSG = e.message
        sendMail()
        for result in results:
           droid_game_until.update(updateSql,(result[1],result[0]))
def sendMail():
    global mailContents
    mailContents = (mailContents + '执行日期：%s\n统计日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), handleDay, ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
#################################################
if __name__=='__main__':
    print "====go %s=="%datetime.datetime.now()
    try:
        #初始化
        init()
        #清除临时表中的数据
        clearData()
        #获取日志文件路径
        getLogPath()
        #PV、UV统计入库
        countPvAndUv()
        updateActivityView()
    except Exception, ex:
        fp = StringIO.StringIO()
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ex
    finally:
        if droid_stat_until: droid_stat_until.close()
        if droid_game_until: droid_game_until.close()
        if ERROR_MSG:
            sendMail()
    print "===over %s==="%datetime.datetime.now()
