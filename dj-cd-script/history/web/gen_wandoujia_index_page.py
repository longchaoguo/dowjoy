#!/usr/bin/python
# -*- #coding:utf-8

__author__ = "$Author: shixuelin $"
__version__ = "$Revision: 1.1 $"
__date__ = "$Date: 2011/03/21 09:57:36 $"

import os
import sys
import re
import urllib2
import datetime

pageData=""
fp=urllib2.urlopen("http://211.147.5.167:8080/wdjandroid/")
if fp.code == urllib2.httplib.OK:
    pageData=fp.read()
    fp.close()
else:
    print "http status error: %s"%(fp.code)
    sys.exit()

#如果获取到的数据大小小于100，则取消本次更新操作
if pageData.find("</html>") < 100:
    print "the original web index page is error! "
    sys.exit()

pageData=re.sub("\ +", " ", pageData)
pageData=re.sub("\\n+", "", pageData)
pageData=re.sub("\\r+", "", pageData)
pageData=re.sub("\\t+", "", pageData)

today=datetime.datetime.today()

nowdate = str(datetime.datetime.strftime(today, "%Y-%m-%d %H:%M:%S"))

pageData=pageData + "<!--" + nowdate + "-->"

filePath = "/usr/local/apache/htdocs/"

tempFileName = "temp_wandoujia_index.html"

fileName = "wandoujia_index.html"

os.system("rm -f %s%s"%(filePath, tempFileName))

fp = file(filePath + tempFileName, 'a+')
fp.write(pageData)
fp.close()

#如果临时文件的文件大小小于1kb，则取消本次更新操作
if os.path.getsize(filePath + tempFileName) < 1000:
    print "the original web index page size is too small! "
    sys.exit()

os.system("mv %s%s  %s%s"%(filePath, tempFileName, filePath, fileName))
    
print "\n update success !!"
    

    
