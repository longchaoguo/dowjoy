#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
#自动删除非法评论
###########################################
import os
import sys
import time
import datetime
import StringIO
import traceback
from djutil.FtpUtil import FtpUtil
from djutil.DBUtil import DBUtil
from djutil.OptsUtil import OptsUtil
from djutil.MailUtil import MailUtil
###########################################
droid_game_10 = DBUtil('droid_game_10')
#####邮件报错提醒
ERROR_MSG = None
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"日志FTP脚本出错".encode("gbk")
mailTo = ['qicheng.meng@downjoy.com']
mailContents = u'Hi: \n'
########################################################
def deleteComment():
    sql="select IMEI from `IMEI` where DATE_SUB(now(), INTERVAL 30 MINUTE) <= CREATED_DATE"
    #sql="select IMEI from `IMEI`"
    rows = droid_game_10.queryList(sql, ())
    for row in rows:
        if row:
            sql1 = "delete from CLIENT_COMMENT_1 where created_by=%s"
            sql2 = "delete from CLIENT_COMMENT_2 where created_by=%s"
            sql3 = "delete from CLIENT_COMMENT_3 where created_by=%s"
            sql4 = "delete from CLIENT_COMMENT_4 where created_by=%s"
            sql5 = "delete from CLIENT_COMMENT_5 where created_by=%s"
            sql6 = "delete from CLIENT_COMMENT_6 where created_by=%s"
            sql7 = "delete from CLIENT_COMMENT_7 where created_by=%s"
            sql8 = "delete from CLIENT_COMMENT_8 where created_by=%s"
            sql9 = "delete from CLIENT_COMMENT_9 where created_by=%s"
            sql10 = "delete from CLIENT_COMMENT_10 where created_by=%s"
            sql11 = "delete from CLIENT_COMMENT_11 where created_by=%s"
            sql12 = "delete from CLIENT_COMMENT_12 where created_by=%s"
            sql13 = "delete from CLIENT_COMMENT_13 where created_by=%s"
            sql14 = "delete from CLIENT_COMMENT_14 where created_by=%s"
            sql15 = "delete from CLIENT_COMMENT_15 where created_by=%s"
            sql16 = "delete from CLIENT_COMMENT_16 where created_by=%s"
            sql17 = "delete from CLIENT_COMMENT_17 where created_by=%s"
            sql18 = "delete from CLIENT_COMMENT_18 where created_by=%s"
            sql19 = "delete from CLIENT_COMMENT_19 where created_by=%s"
            sql20 = "delete from CLIENT_COMMENT_20 where created_by=%s"
            #print str(row[0])
            droid_game_10.delete(sql1, (row[0]))
            droid_game_10.delete(sql2, (row[0]))
            droid_game_10.delete(sql3, (row[0]))
            droid_game_10.delete(sql4, (row[0]))
            droid_game_10.delete(sql5, (row[0]))
            droid_game_10.delete(sql6, (row[0]))
            droid_game_10.delete(sql7, (row[0]))
            droid_game_10.delete(sql8, (row[0]))
            droid_game_10.delete(sql9, (row[0]))
            droid_game_10.delete(sql10, (row[0]))
            droid_game_10.delete(sql11, (row[0]))
            droid_game_10.delete(sql12, (row[0]))
            droid_game_10.delete(sql13, (row[0]))
            droid_game_10.delete(sql14, (row[0]))
            droid_game_10.delete(sql15, (row[0]))
            droid_game_10.delete(sql16, (row[0]))
            droid_game_10.delete(sql17, (row[0]))
            droid_game_10.delete(sql18, (row[0]))
            droid_game_10.delete(sql19, (row[0]))
            droid_game_10.delete(sql20, (row[0]))


###########################################################
if __name__ == '__main__':
    print "=================start %s======" % datetime.datetime.now()
    try:
        #压缩已处理日志文件
        deleteComment()

    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        raise Exception, ERROR_MSG
    finally:
        if droid_game_10: droid_game_10.close()
    print "=================end   %s======" % datetime.datetime.now()


