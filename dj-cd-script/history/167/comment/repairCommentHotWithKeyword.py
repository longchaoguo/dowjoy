#!/usr/bin/python
#encoding=utf-8
'''
Created on 2014年12月10日

@author: qiu.zhong@downjoy.com
# 0.只跑一次，处理老评论数据，（大于指定内容字数（M*E% ）+点赞数+回复数）

'''
import pymongo
import httplib,urllib
import datetime
import time
from bson.code import Code
from bson import ObjectId
import json
import traceback
import StringIO
from djutil.MailUtil import MailUtil
import MySQLdb
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

connection = pymongo.Connection('192.168.0.72',27017)
db = connection.comment
key_hot = "hot"
key_resource = "resourceKey"
key_hotrange = "hr"
key_maxhot = "mh"
key_hotcount = "hc"
key_pubtime= "pubTime"

keywordHost = "comment.d.cn"
keywordPort = 80
api_keyword = "http://comment.d.cn/comment/_i/checkHotKeyword"

# 0. 只跑一次，处理老评论数据，（大于指定内容字数（M*E% ）+点赞数+回复数）
def main():
    #初始化资源热度值
    nowMillseconds = int(time.time() * 1000)
    for out in db.resourceComment.find({"isHot":True}, {"content":1}).batch_size(30):
        content = out["content"]
        if(filterKeyWord(content)):
            db.resourceComment.update({"_id":out["_id"]}, {"$set":{"isHot":False, "time":nowMillseconds}})


def filterKeyWord(content):
    connKeyword = httplib.HTTPConnection(keywordHost, keywordPort)
    form = urllib.urlencode({"content":content})
    headers = {"Content-Type":"application/x-www-form-urlencoded"}
    connKeyword.request(method="POST",url=api_keyword, body=form,headers=headers)
    response = connKeyword.getresponse()
    res= response.read()
    tmp = json.loads(res)
    contains = tmp["check-result"]
    if(contains!=None):
        return contains
    return False

main()   