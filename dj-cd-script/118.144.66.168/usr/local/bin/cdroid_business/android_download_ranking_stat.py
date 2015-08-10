#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: liangshan$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2014/10/20 17:46 $"

#####################################################
#此脚本每天执行一次，将安卓各类下载量top300更新至旧top300表里。
#####################################################
import datetime
import StringIO
import traceback
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil

#初始化参数
handleDay = datetime.datetime.today() - datetime.timedelta(1)
handledate = str(datetime.datetime.strftime(handleDay, "%Y-%m-%d"))
dbUtil_droid_game=DBUtil('droid_game_10')
dbUtil_download_stat=DBUtil('download_stat_168')

#下载排行榜类型
RANKING_TYPE_WEEKLY_GAME_TOP300 = 1
RANKING_TYPE_WEEKLY_SOFTWARE_TOP300 = 2
RANKING_TYPE_MONTHLY_GAME_TOP300 = 4
RANKING_TYPE_TOTAL_GAME_TOP300 = 8
RANKING_TYPE_WEEKLY_NEW_GAME_TOP300 = 16
RANKING_TYPE_WEEKLY_CHINESE_GAME_TOP300 = 32
RANKING_TYPE_WEEKLY_DIGUA_GAME_TOP300 = 64
RANKING_TYPE_WEEKLY_NETGAME_TOP300 = 128
RANKING_TYPE_MONTHLY_NETGAME_TOP300 = 256

#下载排行榜类型描述字典
RANKING_TYPE_DESCRIPTION_DIC = {RANKING_TYPE_WEEKLY_GAME_TOP300:u'游戏周排行榜',RANKING_TYPE_WEEKLY_SOFTWARE_TOP300:u'软件周排行榜', RANKING_TYPE_MONTHLY_GAME_TOP300:u'游戏月排行榜', RANKING_TYPE_TOTAL_GAME_TOP300:u'游戏总排行榜', RANKING_TYPE_WEEKLY_NEW_GAME_TOP300:u'新游周排行榜', RANKING_TYPE_WEEKLY_CHINESE_GAME_TOP300:u'中文游戏周排行榜', RANKING_TYPE_WEEKLY_DIGUA_GAME_TOP300:u'地瓜渠道游戏周排行榜', RANKING_TYPE_WEEKLY_NETGAME_TOP300:u'网游周排行榜', RANKING_TYPE_MONTHLY_NETGAME_TOP300:u'网游月排行榜'}

#地瓜渠道表示
DIGUA_CHANNEL_FLAG = 30

#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"当乐数据中心".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"安卓排行榜统计错误信息".encode("gbk")
mailTo=['shan.liang@downjoy.com']
mailContents=u'Hi: \n'

###############################################
# 清除旧数据
###############################################
def clear(rankingType):
    sql = "delete from DOWNLOAD_RANKING_TOP300 where RANKING_TYPE = %d AND IS_FIXED != 1" %(rankingType)
    dbUtil_droid_game.delete(sql)

###############################################
# 获取人为排序信息(IS_FIXED=1)，分别存放在一个字典和一个列表里。
# 字典以key为资源id,value为资源位置；列表为资源位置的list
###############################################
def getFixedRankingResInfo(rankingType):
    global fixedResDic, fixedResPosList
    fixedResDic = {}
    fixedResPosList = []
    sql = "select RESOURCE_ID, POSITION from DOWNLOAD_RANKING_TOP300 where RANKING_TYPE = %d AND IS_FIXED = 1" % (rankingType)
    rows = dbUtil_droid_game.queryList(sql)
    if not rows:
        return
    for r in rows:
        fixedResDic[r[0]] = r[1]
        fixedResPosList.append(r[1])
    print len(fixedResPosList)
    
###############################################
# 获取自然排序信息
###############################################
def getNaturalRankingResInfo(rankingType):
    global naturalResList
    naturalResList = {}
    sql = ''
    # 排行榜自然排序
    if rankingType == RANKING_TYPE_WEEKLY_GAME_TOP300:
        sql = "select GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where GAME_ID>0 and datediff('%s', CREATED_DATE)>0 and datediff('%s', CREATED_DATE)<=7 and RESOURCE_TYPE=1 group by GAME_ID order by CNT desc limit 300" % (handledate, handledate)
    elif rankingType == RANKING_TYPE_WEEKLY_SOFTWARE_TOP300:
        sql = "select GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where GAME_ID>0 and datediff('%s', CREATED_DATE)>0 and datediff('%s', CREATED_DATE)<=7 and RESOURCE_TYPE=2 group by GAME_ID order by CNT desc limit 300" % (handledate, handledate)
    elif rankingType == RANKING_TYPE_MONTHLY_GAME_TOP300:
        sql = "select GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where GAME_ID>0 and datediff('%s', CREATED_DATE)>0 and datediff('%s', CREATED_DATE)<=30 and RESOURCE_TYPE=1 group by GAME_ID order by CNT desc limit 300" % (handledate, handledate)
    elif rankingType == RANKING_TYPE_TOTAL_GAME_TOP300:
        sql = "select GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where GAME_ID>0 and RESOURCE_TYPE=1 group by GAME_ID order by CNT desc limit 300"
    elif rankingType == RANKING_TYPE_WEEKLY_NEW_GAME_TOP300:
        gameIds = ''
        newGame_sql = "SELECT G.ID FROM GAME G INNER JOIN GAME_PKG GP ON G.ID = GP.GAME_ID WHERE G.RESOURCE_TYPE = 1 AND G.STATUS=1 AND GP.ID = (SELECT MAX(ID) FROM  GAME_PKG GP2 WHERE GP2.GAME_ID = G.ID) AND DATEDIFF(%s, GP.CREATED_DATE)>0 AND DATEDIFF(%s, GP.CREATED_DATE)<=7"
        rows = dbUtil_droid_game.queryList(newGame_sql, (handledate, handledate))
        if not rows:
            return
        for row in rows:
            gameIds = gameIds + str(row[0]) + ','
        gameIds = gameIds[:-1]
        sql = "select GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where datediff('%s', CREATED_DATE)>0 and datediff('%s', CREATED_DATE)<=7 and RESOURCE_TYPE=1 and GAME_ID IN (" % (handledate, handledate) + gameIds + ") group by GAME_ID order by CNT desc limit 300"
    elif rankingType == RANKING_TYPE_WEEKLY_CHINESE_GAME_TOP300:
        gameIds = ''
        chineseGame_sql = "SELECT ID FROM GAME G WHERE G.RESOURCE_TYPE = 1 AND G.STATUS=1 AND G.LANGUAGE_TYPE = 2"
        rows = dbUtil_droid_game.queryList(chineseGame_sql)
        if not rows:
            return
        for row in rows:
            gameIds = gameIds + str(row[0]) + ','
        gameIds = gameIds[:-1]
        sql = "select GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where datediff('%s', CREATED_DATE)>0 and datediff('%s', CREATED_DATE)<=7 and RESOURCE_TYPE=1 and GAME_ID IN (" % (handledate, handledate) + gameIds + ") group by GAME_ID order by CNT desc limit 300"
    elif rankingType == RANKING_TYPE_WEEKLY_DIGUA_GAME_TOP300:
        sql = "select GAME_ID, RESOURCE_TYPE, sum(DOWNS) as CNT from ANDROID_GAME_DOWNLOAD_DAILY where GAME_ID>0 and datediff('%s', CREATED_DATE)>0 and datediff('%s', CREATED_DATE)<=7 and RESOURCE_TYPE=1 and CHANNEL_FLAG = 30 group by GAME_ID order by CNT desc limit 300" % (handledate, handledate)
    elif rankingType == RANKING_TYPE_WEEKLY_NETGAME_TOP300:
        sql = "select WEEK_CHANNEL_ID, 5, WEEK_DOWNS from NETGAME_DOWN_STAT"
    elif rankingType == RANKING_TYPE_MONTHLY_NETGAME_TOP300:
        sql = "SELECT MONTH_CHANNEL_ID, 5, MONTH_DOWNS FROM NETGAME_DOWN_STAT"
    else:
        return
    
    # 游戏、软件与网游下载量的数据库来源不同
    if ((rankingType == RANKING_TYPE_WEEKLY_GAME_TOP300) or (rankingType == RANKING_TYPE_WEEKLY_SOFTWARE_TOP300) or 
        (rankingType == RANKING_TYPE_MONTHLY_GAME_TOP300) or (rankingType == RANKING_TYPE_TOTAL_GAME_TOP300) or 
        (rankingType == RANKING_TYPE_WEEKLY_NEW_GAME_TOP300) or (rankingType == RANKING_TYPE_WEEKLY_CHINESE_GAME_TOP300) or 
        (rankingType == RANKING_TYPE_WEEKLY_DIGUA_GAME_TOP300)):
        naturalResList = dbUtil_download_stat.queryList(sql)
    else:
        naturalResList = dbUtil_droid_game.queryList(sql)
    print len(naturalResList)

###############################################
# 综合自然排序和人为排序，插入最终的排序
###############################################
def getRankingResInfo(rankingType):
    curPos = 1
    for resInfo in naturalResList:
        #排除一些特定厂商的游戏
        if ((rankingType == RANKING_TYPE_WEEKLY_GAME_TOP300) or (rankingType == RANKING_TYPE_WEEKLY_SOFTWARE_TOP300) or 
        (rankingType == RANKING_TYPE_MONTHLY_GAME_TOP300) or (rankingType == RANKING_TYPE_TOTAL_GAME_TOP300) or 
        (rankingType == RANKING_TYPE_WEEKLY_NEW_GAME_TOP300) or (rankingType == RANKING_TYPE_WEEKLY_CHINESE_GAME_TOP300) or 
        (rankingType == RANKING_TYPE_WEEKLY_DIGUA_GAME_TOP300)):
            vendorId = getVendorIdByGameId(resInfo[0])
            if (vendorId == 0) or (vendorId == 9) or (vendorId == 49):
                continue
        #排序
        if resInfo[0] in fixedResDic:
            position = fixedResDic[resInfo[0]]
            sql="update DOWNLOAD_RANKING_TOP300 set RESOURCE_TYPE=%d,CNT=%s,POSITION=%s,STAT_DATE='%s',RANKING_DESCRIPTION='%s' where RESOURCE_ID=%s and RANKING_TYPE = %d" % (resInfo[1], resInfo[2],position,handledate,RANKING_TYPE_DESCRIPTION_DIC[rankingType], resInfo[0], rankingType)
            dbUtil_droid_game.update(sql)
        else:
            while True :
                if curPos not in fixedResPosList:
                    sql = "insert into DOWNLOAD_RANKING_TOP300(RESOURCE_ID, RESOURCE_TYPE, CNT, POSITION, STAT_DATE, RANKING_TYPE, RANKING_DESCRIPTION) values(%s, %d, %s, %s, '%s', %d, '%s')" % (resInfo[0], resInfo[1], resInfo[2], curPos, handledate, rankingType, RANKING_TYPE_DESCRIPTION_DIC[rankingType])
                    dbUtil_droid_game.insert(sql)
                    curPos = curPos + 1
                    break
                else:
                    curPos = curPos + 1
        if curPos > 300:
            break
    
###############################################  
#查询厂商ID 
###############################################
def getVendorIdByGameId(gameId):
    sql="select VENDOR_ID from GAME where ID = %d" % gameId
    rs = dbUtil_droid_game.queryRow(sql)
    try:
        vendorId=rs[0]
    except:
        vendorId=0
    return vendorId      
    
####################################
# 根据排行榜类型获取排行榜数据
####################################
def handleRanking(rankingType):
    # 清除旧数据
    clear(rankingType)
    
    # 获取人为排序信息
    getFixedRankingResInfo(rankingType)
    
    # 获取自然排行榜信息
    getNaturalRankingResInfo(rankingType)
    
    # 综合自然排序和人为排序，插入最终的排序结果
    getRankingResInfo(rankingType)

#邮件
def sendMail():
    global mailContents
    mailContents=(mailContents+u'下载量排行榜统计脚本执行出错，\n错误信息：%s\n谢谢'%(ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)
    
if __name__ == "__main__":
    print "=============start %s===="%datetime.datetime.now()
    try:
        #游戏周排行榜
        handleRanking(RANKING_TYPE_WEEKLY_GAME_TOP300)
        
        #软件周排行榜
        handleRanking(RANKING_TYPE_WEEKLY_SOFTWARE_TOP300)
        
        #游戏月排行榜
        handleRanking(RANKING_TYPE_MONTHLY_GAME_TOP300)
        
        #游戏总排行榜
        handleRanking(RANKING_TYPE_TOTAL_GAME_TOP300)
        
        #新游周排行榜
        handleRanking(RANKING_TYPE_WEEKLY_NEW_GAME_TOP300)
        
        #中文周排行榜
        handleRanking(RANKING_TYPE_WEEKLY_CHINESE_GAME_TOP300)
        
        #地瓜渠道周排行榜
        handleRanking(RANKING_TYPE_WEEKLY_DIGUA_GAME_TOP300)
        
        #网游周排行榜
        handleRanking(RANKING_TYPE_WEEKLY_NETGAME_TOP300)
        
        #网游月排行榜
        handleRanking(RANKING_TYPE_MONTHLY_NETGAME_TOP300)
        
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