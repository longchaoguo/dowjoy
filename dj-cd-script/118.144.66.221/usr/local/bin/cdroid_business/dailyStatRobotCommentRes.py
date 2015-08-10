#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014年12月11日

@author: qiu.zhong@downjoy.com

# crontab 设置定时执行
30 1 * * * /usr/local/bin/pyscript/comment/dailyStatCommentRank.py >> /home/downjoy/logs/py_dailyStatCommentRank.log &

每天新增评论，对应等级应用占评论应用的比例
每天新增评论，对应等级应用接收到评论数的比例

'''
import pymongo
import datetime
import time
import traceback
import StringIO
from djutil.MailUtil import MailUtil

# connection = pymongo.Connection('192.168.0.72',27017)
# dbComment = connection.comment
# dbRobotComment = connection.robotComment

connection = pymongo.MongoClient('192.168.9.25',27017)
dbComment = connection.comment
dbComment.authenticate('moster','shzygjrmdwg')
dbRobotComment = connection.robotCommentSchedular
dbRobotComment.authenticate('moster','shzygjrmdwg')

#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"评论系统衰减值计算错误信息（dailyStatResCommentHot.py）".encode("gbk")
mailTo = ['qiu.zhong@downjoy.com']
mailContents = u'Hi: \n'

today = datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
monthStr = str(datetime.date.today().month)
if(len(monthStr)==1):
    monthStr = "0"+monthStr
dayStr = str(datetime.date.today().day)
if(len(dayStr)==1):
    dayStr = "0"+dayStr
intToday = int(str(datetime.date.today().year) + monthStr + dayStr)
intOneWeekAgo = int(str(today + datetime.timedelta(days=-7)).replace("-",""))
yestoday = today + datetime.timedelta(days=-1)
todayMilliSeconds = int(time.mktime(time.strptime(str(today), "%Y-%m-%d"))) * 1000
yestodayMilliSeconds =  int(time.mktime(time.strptime(str(yestoday), "%Y-%m-%d"))) * 1000

# 每天新增评论，对应等级应用占评论应用的比例
# 每天新增评论，对应等级应用接收到评论数的比例
# 两个统计存一行数据，保证原子性
def main():
    # 每天新增评论，对应等级应用接收到评论数的比例
    countLevel1Comment = 0
    countLevel2Comment = 0
    countLevel3Comment = 0
    for out in dbComment.resourceComment.find({"opTime":{"$gte":yestodayMilliSeconds, "$lte":todayMilliSeconds}},{"resourceKey":1}):
        resourceKey = out["resourceKey"]
        keys = resourceKey.split(":")
        rid = int(keys[0])
        rtype = int(keys[1])
        rlObj = dbRobotComment.robotUrlMappingInfo.find_one({"rid":rid, "rt":rtype},{"rl":1})
        if(rlObj):
            rl = rlObj["rl"]
            if(rl==1):
                countLevel1Comment+=1
            elif(rl==2):
                countLevel2Comment+=1
            elif(rl==3):
                countLevel3Comment+=1
#             print str(rid)+":"+str(rtype)+":"+str(rl)
    totalComment = countLevel1Comment + countLevel2Comment + countLevel3Comment  
    percentLevel1Comment = 0
    percentLevel2Comment = 0
    percentLevel3Comment = 0
    if(totalComment>0):
        percentLevel1Comment = float(countLevel1Comment) / totalComment
        percentLevel2Comment = float(countLevel2Comment) / totalComment
        percentLevel3Comment = float(countLevel3Comment) / totalComment
        
    # 每天新增评论，对应等级应用占评论应用的比例
    countLevel1Res = 0
    countLevel2Res = 0
    countLevel3Res = 0    
    for out in dbComment.resourceComment.find({"opTime":{"$gte":yestodayMilliSeconds, "$lte":todayMilliSeconds}},{"resourceKey":1}).distinct('resourceKey'):
        resourceKey = out
        keys = resourceKey.split(":")
        rid = int(keys[0])
        rtype = int(keys[1])
        rlObj = dbRobotComment.robotUrlMappingInfo.find_one({"rid":rid, "rt":rtype},{"rl":1})
        if(rlObj):
            rl = rlObj["rl"]
            if(rl==1):
                countLevel1Res+=1
            elif(rl==2):
                countLevel2Res+=1
            elif(rl==3):
                countLevel3Res+=1
#     totalRes = countLevel1Res + countLevel2Res + countLevel3Res  
#     percentLevel1Res = 0
#     percentLevel2Res = 0
#     percentLevel3Res = 0
#     if(totalRes>0):
#         percentLevel1Res = float(countLevel1Res) / totalRes
#         percentLevel2Res = float(countLevel2Res) / totalRes
#         percentLevel3Res = float(countLevel3Res) / totalRes
    
        
    # TODO 两个统计存一行数据，保证原子性
    insert = { 
              "percentLevel1Comment":percentLevel1Comment, "percentLevel2Comment":percentLevel2Comment, "percentLevel3Comment":percentLevel3Comment,
              "countLevel1Res":countLevel1Res, "countLevel2Res":countLevel2Res, "countLevel3Res":countLevel3Res}
    dbRobotComment.robotDailyStat.update({"_id":intToday}, insert, True)
    
def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

###############################################################
if __name__ == '__main__':
    try:
        main()
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if connection:
            connection.close()
        if ERROR_MSG:
            sendMail()

