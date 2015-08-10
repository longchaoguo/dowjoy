#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2015/01/20 $"

################################################
#����������android����ϵͳͷ����
################################################

import sys
import codecs
import os
import datetime
import MySQLdb
import pymongo
import re
import StringIO
import traceback

# mongodb��������
mongoCon = pymongo.MongoClient("192.168.0.72", 27017)
mdb = mongoCon.communication

def update():
    rows = mdb.comm_user_feed.find()
    for row in rows:
        id = row["_id"]
        photo = "http://tools.service.d.cn/userhead/get?mid=" + str(id) + "&size=middle"
        mdb.comm_user_feed.update({"_id" : id}, {'$set' : {'photo' : photo}})
            
###############################################################
if __name__ == '__main__':
    try:
        #��¼��ʼʱ��
        startTime = datetime.datetime.now()
        
        update()
        
        #��¼�ܹ�����ʱ��
        spentTime = datetime.datetime.now() - startTime
        print '����ϵͳͷ���޸ģ�' + str(spentTime)
    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
        print ex
    finally:
        mongoCon.close()
