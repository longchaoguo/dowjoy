#!/usr/bin/python
#-*-#coding: cp936

################################################
#功能描述：网游下载量统计，
#依赖download_stat.ANDROID_GAME_DOWNLOAD_DAILY表数据
################################################
import datetime
import sys
import StringIO
import traceback
from djutil.OptsUtil import OptsUtil
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

#####邮件报错提醒
ERROR_MSG=None
mailServer = "mail.downjoy.com"
mailFromName=u"当乐数据中心".encode("gbk")
mailFromAddr="webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject=u"网游下载量统计错误信息".encode("gbk")
mailTo=['zhou.wu@downjoy.com','guoqiang.sun@downjoy.com']
mailContents=u'Hi: \n'
#############################################

#数据库连接
download_stat_168 = DBUtil('download_stat_168')
droid_stat_168 = DBUtil('droid_stat_168')


CHANNEL_FLAG_LIST = {'10':u'web',
                     '20':u'wap',
                     '30':u'地瓜',
                     '40':u'360合作',
                     '50':u'360一键',
                     '60':u'豌豆荚合作',
                     '70':u'豌豆荚一键',
                     '80':u'百度',
                     '90':u'腾讯soso',
                     '100':u'腾讯一键',
                     '110':u'腾讯专区',
                     '120':u'多特合作',
                     '130':u'360聚合',
                     '140':u'PC版地瓜',
                     '150':u'PC版地瓜一键',
                     }

DOWNS_DETAIL_LIST = {1:0,
                     2:0,
                     5:0,
                     10:0,
                     20:0,
                     30:0,
                     40:0,
                     50:0,
                     60:0,
                     70:0,
                     80:0,
                     90:0,
                     100:0,
                     110:0,
                     120:0,
                     130:0,
                     140:0,
                     150:0,
                     }


GAME_NAME_LIST = {}

#################################################


'''
@param handledate: yyyy-MM-dd形式的日期字符串
'''
def cleanData(handledate):
    sql="delete from NETGAME_DOWNLOAD_DAILY_SUM where STAT_DATE = '%s'"%(handledate)
    droid_stat_168.delete(sql)

'''
@param handledate: yyyy-MM-dd形式的日期字符串
'''
def statDownsSum(handledate):
    sql = "select sum(downs) from ANDROID_GAME_DOWNLOAD_DAILY where resource_type=5 and CREATED_DATE = '%s'"%(handledate)
    downs = download_stat_168.queryCount(sql)
    
    sql = '''SELECT CHANNEL_FLAG,sum(downs) FROM ANDROID_GAME_DOWNLOAD_DAILY
             where resource_type=5 and CREATED_DATE = '%s' group by CHANNEL_FLAG '''%(handledate)
    rows = download_stat_168.queryList(sql)
    DOWNS_DETAIL_LIST = {}
    for row in rows:
        DOWNS_DETAIL_LIST[int(row[0])]=row[1]
    detailDowns =""
    if DOWNS_DETAIL_LIST.has_key(10):
        detailDowns = detailDowns + str(DOWNS_DETAIL_LIST.get(10))
    else:
        detailDowns = detailDowns + str(0)
    if DOWNS_DETAIL_LIST.has_key(30):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(30))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(40):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(40))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(50):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(50))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(60):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(60))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(70):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(70))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(80):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(80))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(90):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(90))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(100):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(100))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(110):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(110))
    else:
        detailDowns = detailDowns + ":" + str(0)
    if DOWNS_DETAIL_LIST.has_key(140):
        detailDowns = detailDowns + ":" + str(DOWNS_DETAIL_LIST.get(140))
    else:
        detailDowns = detailDowns + ":" + str(0)
    
    sql = "insert into NETGAME_DOWNLOAD_DAILY_SUM (DOWNS, DETAIL_DOWNS, STAT_DATE) values(%s,%s,%s)"
    droid_stat_168.insert(sql, (downs, detailDowns, handledate))





def sendMail():
    global mailContents
    mailContents=(mailContents+u'下载量统计脚本执行出错，\n错误信息：%s\n谢谢'%(ERROR_MSG)).encode('gbk')
    mail=MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

#############################################
if __name__ == '__main__':
    try:
        print "netgame_download_stat.py=============start %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))
        opts = OptsUtil.getOpts(sys.argv)
        if not opts or not opts.get('--FILE_DATE'):
            fileDate = datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days = 2), '%Y-%m-%d')
            print fileDate
        else:
            fileDate = opts.get('--FILE_DATE')
        handledate = datetime.datetime.strftime(datetime.datetime.strptime(fileDate, '%Y-%m-%d'), "%Y-%m-%d")
        print "stat date : %s"%(handledate)
        cleanData(handledate)
        statDownsSum(handledate)
        
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file=fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if download_stat_168: 
            download_stat_168.close()
        if droid_stat_168: 
            droid_stat_168.close()
        if ERROR_MSG:
            sendMail()
        print "netgame_download_stat.py=============end %s"%(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"))


