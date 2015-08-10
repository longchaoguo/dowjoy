#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2013/11/13 17:37:45 $"
################################################
#�����������շ���Ϸ(���к�����Ϸ)������ͳ�ƣ�
#����download_stat.ANDROID_GAME_DOWNLOAD_DAILY������
################################################
import datetime
import sys
from djutil.OptsUtil import OptsUtil
from djutil.DBUtil import DBUtil
#####################ȫ�ֱ���####################
#���ݿ�����
dbUtil_187 = DBUtil('download_stat_187')
dbUtil_187_droid = DBUtil('droid_stat_187')
dbUtil_10=DBUtil('droid_game_10')

#��ʼ������
RESOURCE_TYPE_LIST = {'1':u'����','2':u'���','5':u'����'}

CHANNEL_FLAG_LIST = {'10':u'web','20':u'wap','30':u'�ع�','40':u'360����','41':u'360�����Ĺ���','50':u'360һ��','60':u'�㶹�Ժ���','61':u'�㶹�Ժ����Ĺ���','70':u'�㶹��һ��','80':u'�ٶ�','81':u'�ٶȵĹ���','90':u'��Ѷsoso','91':u'��Ѷsoso�Ĺ���','100':u'��Ѷһ��','110':u'��Ѷר��','111':u'��Ѷר���Ĺ���','120':u'���غ���','121':u'���غ����Ĺ���','130':u'360�ۺ�','131':u'360�ۺϵĹ���','140':u'Ѹ�׺���'}

DOWNS_DETAIL_LIST = {1:0,2:0,5:0,10:0,20:0,30:0,40:0,41:0,50:0,60:0,61:0,70:0,80:0,81:0,90:0,91:0,100:0,110:0,111:0,120:0,121:0,130:0,131:0,140:0}

#DOWNS_DETAIL_LIST = {'1':0,'2':0,'5':0,'10':0,'20':0,'30':0,'40':0,'41':0,'50':0,'60':0,'61':0,'70':0,'80':0,'81':0,'90':0,'91':0,'100':0,'110':0,'111':0,'120':0,'121':0,'130':0,'131':0,'140':0}

GAME_NAME_LIST = {}

GAME_IDS = ""
#################################################

def init():
    global handledate
    opts = OptsUtil.getOpts(sys.argv)
    if not opts or not opts.get('--FILE_DATE'):
        fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 2), '%Y-%m-%d')
        print fileDate
    else:
        fileDate = opts.get('--FILE_DATE')
    handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")

def cleanData():
    sql="delete from COOPERATION_GAME_DOWNLOAD_DAILY where datediff(%s, STAT_DATE) = 0"
    dbUtil_187_droid.delete(sql, (handledate))

def statDowns():
    sql = "SELECT GAME_ID, RESOURCE_TYPE, CHANNEL_FLAG, DOWNS, CREATED_DATE  FROM ANDROID_GAME_DOWNLOAD_DAILY WHERE GAME_ID IN (%s) AND datediff('%s', created_date)=0"%(GAME_IDS, handledate)
    rows = dbUtil_187.queryList(sql, ())
    insertsql = "insert into COOPERATION_GAME_DOWNLOAD_DAILY (GAME_ID, GAME_NAME, RESOURCE_TYPE, RESOURCE_TYPE_NAME, CHANNEL_FLAG, CHANNEL_FLAG_NAME, DOWNS, STAT_DATE) values(%s, %s, %s, %s, %s, %s, %s, %s)"
    datalist = []
    for row in rows:
        if not row:
            continue
        try:
            datalist.append((row[0], GAME_NAME_LIST[str(row[0])], row[1], RESOURCE_TYPE_LIST[str(row[1])], row[2], CHANNEL_FLAG_LIST[str(row[2])], row[3], row[4]))
        except:
            continue
        if len(datalist) > 1000:
            insertData(dbUtil_187_droid, insertsql, datalist)
            datalist = []
    if datalist:
        insertData(dbUtil_187_droid, insertsql, datalist)
        datalist = []

def statDownsSum():
    sql = "select sum(downs) from COOPERATION_GAME_DOWNLOAD_DAILY where datediff(%s, stat_date)=0"
    downs = dbUtil_187_droid.queryCount(sql, (handledate))
    sql = "select RESOURCE_TYPE, sum(downs) from COOPERATION_GAME_DOWNLOAD_DAILY where datediff(%s, stat_date)=0 group by RESOURCE_TYPE"
    rows = dbUtil_187_droid.queryList(sql, (handledate))
    for row in rows:
        DOWNS_DETAIL_LIST[int(row[0])]=row[1]
    sql = "select CHANNEL_FLAG, sum(downs) from COOPERATION_GAME_DOWNLOAD_DAILY where datediff(%s, stat_date)=0 group by CHANNEL_FLAG"
    rows = dbUtil_187_droid.queryList(sql, (handledate))
    for row in rows:
        DOWNS_DETAIL_LIST[int(row[0])]=row[1]
    detailDowns = ""
    #DOWNS_DETAIL_LIST=sorted(DOWNS_DETAIL_LIST.items(), key=lambda d: d[0])
    i=1
    for k in sorted(DOWNS_DETAIL_LIST.keys()):
        detailDowns=detailDowns+str(DOWNS_DETAIL_LIST[k])
        if i!=len(DOWNS_DETAIL_LIST):
            detailDowns=detailDowns+":"
        i=i+1
    sql = "insert into COOPERATION_GAME_DOWNLOAD_DAILY_SUM (DOWNS, DETAIL_DOWNS, STAT_DATE) values(%s,%s,%s)"
    dbUtil_187_droid.insert(sql, (downs, detailDowns, handledate))


def initGameData():
    sql="SELECT ID, NAME FROM GAME WHERE DATA_TYPE&4=4"
    rows = dbUtil_10.queryList(sql, ())
    global GAME_IDS
    for row in rows:
        gameId = str(row[0])
        if len(GAME_IDS) != 0:
            GAME_IDS = GAME_IDS + ',' + gameId
        else:
            GAME_IDS = gameId
        GAME_NAME_LIST[gameId] = row[1]

def insertData(dbUtil, sql, dataList):
    try:
        dbUtil.insertMany(sql, tuple(dataList))
    except:
        for data in dataList:
            try:
                dbUtil.insert(sql, data)
            except:
                pass

def main():
    print "===start time %s" % datetime.datetime.now()
    init()
    #initGameData()
    #cleanData()
    #statDowns()
    statDownsSum()

if __name__ == "__main__":
    try:
        main()
    finally:
        if dbUtil_187: dbUtil_187.close()
        if dbUtil_187_droid: dbUtil_187_droid.close()
        if dbUtil_10: dbUtil_10.close()
    print "===over time %s" % datetime.datetime.now()

