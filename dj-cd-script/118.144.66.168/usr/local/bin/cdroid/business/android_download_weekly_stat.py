#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: wenxin$"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2012/09/10 17:46 $"
__modifier__ = "qi.fu@downjoy.com"
__modifydate__ = "$Date: 2012/09/11 17:00 $"

#####################################################
#�˽ű�ÿ��һִ��һ�Σ�����׿������top300��������top300�����187����cronrabÿ��һ������
#####################################################
import datetime
from djutil.DBUtil import DBUtil
from djutil.ScriptExecuteUtil import ScriptExecuteUtil

handleDay = datetime.datetime.today() - datetime.timedelta(1)
handledate = str(datetime.datetime.strftime(handleDay, "%Y-%m-%d"))
#���ݻָ�
#handledate='2012-05-22'
#dbUtilGame=DBUtil('droid_game_10')
#dbUtilDownload=DBUtil('download_stat_187')
#dbUtilStat = DBUtil('stat_187') 

#dbUtilGame=DBUtil('droid_game_test')
dbUtilGame=DBUtil('droid_game_10')
dbUtilDownload=DBUtil('download_stat_168')

#execute = ScriptExecuteUtil(dbUtil=dbUtilStat,handleDate=handleDay)
#####################################################
#ÿ��һ��һ���ڵ�������top300��������top300����
def updateWeeklyData(type):
    table = ""
    if type==1:#��Ϸ
        table = "DOWNLOAD_WEEKLY_GAME_TOP300"
    elif type == 2:#���
        table = "DOWNLOAD_WEEKLY_SOFTWARE_TOP300"
    sql = "delete from %s where IS_FIXED != 1" %(table)
    #ɾ������Ҫ����������
    dbUtilGame.delete(sql)
    #��ѯ������������(IS_FIXED=1)������һ���ֵ��keyΪ��Ϸid,valueΪ��Ϸ�����Ϣ.��Ϸid����һlist��
    sql = "select GAME_ID, POSITION, IS_FIXED from %s where IS_FIXED=1" % (table)
    isFixedRows = dbUtilGame.queryList(sql);
    isFixedGameIdList = []
    isFixedGameDic = {}
    if isFixedRows:
        for r in isFixedRows:
            isFixedGameIdList.append(r[0])
            dic = {}
            dic["gameId"] = r[0]
            dic["position"] = r[1]
            isFixedGameDic[r[0]] = dic
    sql = "select GAME_ID, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where GAME_ID>0 and datediff(%s, CREATED_DATE)>0 and datediff(%s, CREATED_DATE)<=7 and RESOURCE_TYPE=%s group by GAME_ID order by CNT desc limit 300"
    last6Day = getLast6Day(handledate)
    nextDay = getNextDay(handledate)
    rows=dbUtilDownload.queryList(sql, (handledate, handledate, type))
    sql = "select count(*) from %s where IS_FIXED=1" % (table)
    count = dbUtilGame.queryRow(sql)
    maxCount = 300 - count[0]
    i = 0
    #ѭ��������������Ϸ����
    if not rows:
        return
    for row in rows:
        vendorId=getVendorIdByGameId(row[0])
        if vendorId != 0 and vendorId != 9 and vendorId != 49:
            sql="insert into %s (GAME_ID, CNT, STAT_DATE) values(%s, %s, '%s')" % (table,row[0], row[1], handledate)
            if row[0] in isFixedGameIdList:
                dic = isFixedGameDic[row[0]]
                position = dic["position"]
                sql="update %s set CNT=%s,POSITION=%s,STAT_DATE='%s' where GAME_ID=%s" % (table,row[1],position,handledate,row[0])
                dbUtilGame.update(sql)
            else:
                dbUtilGame.insert(sql)
                i = i + 1
        if i >= maxCount:
            break
    fillPosition(type)

def fillPosition(type):#�������
    table = ""
    if type == 1:#��Ϸ
        table = "DOWNLOAD_WEEKLY_GAME_TOP300"
    elif type == 2:#���
        table = "DOWNLOAD_WEEKLY_SOFTWARE_TOP300"
    selectSql = "select * from %s where IS_FIXED = 0 order by CNT desc" % (table)
    rows = dbUtilGame.queryList(selectSql)
    i = 1
    if not rows:
        return 
    for row in rows:
        while True :
            sql = "select * from %s where POSITION=%s" % (table,i)
            count = dbUtilGame.queryRow(sql)
            if  not count:
                updateSql = "update %s set POSITION=%s where GAME_ID=%s" % (table,i,row[0])
                dbUtilGame.update(updateSql)
                i = i + 1
                break
            else:
                i = i + 1

def getVendorIdByGameId(gameId):
    sql="select VENDOR_ID from GAME where ID = %s"
    rs=dbUtilGame.queryRow(sql, (gameId))
    try:
        vendorId=rs[0]
    except:
        vendorId=0
    return vendorId

def getLast6Day(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime(datetime.datetime.strptime(dayStr, formatStr)-datetime.timedelta(days=6), formatStr)

def getNextDay(dayStr, formatStr='%Y-%m-%d'):
    return datetime.datetime.strftime(datetime.datetime.strptime(dayStr, formatStr)+datetime.timedelta(days=1), formatStr)

def main():
    print "=============start %s===="%datetime.datetime.now()
    #������Ϸ�������б�
    updateWeeklyData(1)
    #��������������б�
    updateWeeklyData(2)
    print "=============end   %s===="%datetime.datetime.now()

if __name__ == "__main__":
    try:
        main()
    finally:
        #if dbUtilStat: dbUtilStat.close()
        if dbUtilGame: dbUtilGame.close()
        if dbUtilDownload: dbUtilDownload.close()
