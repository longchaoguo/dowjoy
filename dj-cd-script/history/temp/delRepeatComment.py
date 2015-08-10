#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014��12��10��

@author: qiu.zhong@downjoy.com
# ɾ���ظ�����

'''
import pymongo
import time
import MySQLdb
import datetime
import StringIO
import traceback

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.comment
key_hot = "hot"
key_resource = "resourceKey"
key_hotrange = "hr"
key_maxhot = "mh"
key_hotcount = "hc"
key_pubtime= "pubTime"

def main():
    count = 0
    totalCnt = db.resourceComment.find().count()
    print "ԭʼ����������" + str(totalCnt)
    for out in db.resourceComment.distinct(key_resource):
        resourceKey = out
        checked = set()
        for out in db.resourceComment.find({"resourceKey":resourceKey}, {"_id":1, "opTime":1, "content":1}).sort("_id",pymongo.DESCENDING):
            content = out["content"]
            opTime = out["opTime"]
            id = out["_id"]
            repeatIds = db.resourceComment.find({"resourceKey":resourceKey, "content":content, "opTime":opTime}, {"_id":1}).sort("_id",pymongo.ASCENDING)
            repeatId = repeatIds[0]["_id"]
            if(repeatId in checked):
                continue
            if(id!=repeatId):
                db.resourceComment.remove({"_id":id})
                checked.add(repeatId)
                count = count + 1
    print "ɾ����������" + str(count)
    totalCnt = db.resourceComment.find().count()
    print "ʣ������������" + str(totalCnt)

try:    
    #��¼��ʼʱ��
    print "===============delete repeat comment start =================="
    startTime = datetime.datetime.now()    
                
    main() 

    #��¼�ܹ�����ʱ��
    spentTime = datetime.datetime.now() - startTime
    print 'ɾ���ظ����ۻ���ʱ�䣺' + str(spentTime)
    print "===============delete repeat comment end =================="
except Exception, ex:
    print ex
    fp = StringIO.StringIO()    #�����ڴ��ļ�����
    traceback.print_exc(file = fp)
    ERROR_MSG = str(fp.getvalue())
    print ERROR_MSG
finally:
    connection.close()





