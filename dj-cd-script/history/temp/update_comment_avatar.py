#!/usr/bin/python
#-*-#coding: cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2015/01/20 $"

################################################
#功能描述：android评论头像处理
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

# mongodb链接设置
mongoCon = pymongo.MongoClient("192.168.0.72", 27017)
mdb = mongoCon.comment

def update():
   # rows = mdb.resourceComment.find({"$or": [{"_id":2488112}, {"_id": 2488113}, {"_id": 1}, {"_id": 1672102}, {"_id": 1672197}, {1569512}, {2480162}]})
    rows = mdb.resourceComment.find().sort("_id",pymongo.ASCENDING)
    global count
    count = 0
    for row in rows:
        count += 1
        id = row["_id"]
        try:
            avatarUrl = getUserAvatar(row)
            if row.has_key("subComments") and (row["subComments"] != None) and len(row["subComments"]) > 0:
                newSubComments = []
                for subComment in row["subComments"]:
                    if not subComment:
                        continue
                    subComment["avatarUrl"] = getUserAvatar(subComment)
                    newSubComments.append(subComment)
                mdb.resourceComment.update({"_id" : id}, {'$set' : {'avatarUrl' : avatarUrl, 'subComments' : newSubComments}})
            else:
                mdb.resourceComment.update({"_id" : id}, {'$set' : {'avatarUrl' : avatarUrl}})
        except Exception, ex:
            fp = StringIO.StringIO()    #创建内存文件对象
            traceback.print_exc(file = fp)
            ERROR_MSG = str(fp.getvalue())
            print id
            print ERROR_MSG
            print ex
    print count        
def getUserAvatar(row):
    pattern = re.compile('\d+')
    if (row.has_key("user") and pattern.match(row["user"].strip())):
        mid = row["user"].strip()
        if (len(mid) <= 10):
            avatarUrl = "http://tools.service.d.cn/userhead/get?mid=" + mid + "&size=middle"
        else:
            avatarUrl = "http://raw.android.d.cn/cdroid_res/web/common/avatar.jpg"
    else:
        avatarUrl = "http://raw.android.d.cn/cdroid_res/web/common/avatar.jpg"
        
    return avatarUrl
            
###############################################################
if __name__ == '__main__':
    try:
        #记录开始时间
        print "===============comment update start =================="
        startTime = datetime.datetime.now()
        
        update()
        
        #记录总共花销时间
        spentTime = datetime.datetime.now() - startTime
        print '评论系统头像修改：' + str(spentTime)
        print "===============comment update end =================="
    except Exception, ex:
        print count
        print ex
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        print ERROR_MSG
    finally:
        mongoCon.close()


