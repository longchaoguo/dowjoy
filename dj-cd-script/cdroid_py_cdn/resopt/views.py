#!/usr/bin/python
# -*- #coding:UTF-8
__author__ = "$Author: helin $"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/07/11 16:51:57 $"

from django.template import loader, Context
from django.http import HttpResponse
import hashlib
import os
import time
import datetime
import urllib

PASSWD = "41eacdf914ac456cabecf584e93f299c"



def md5hex(word):
    """ MD5加密算法，返回32位小写16进制符号 """
    if isinstance(word, unicode):
        word = word.encode("utf-8")
    elif not isinstance(word, str):
        word = str(word)
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()

def getFileSize(request):
    """获取cdn源站上的文件大小，用于检测同步是否完成"""
    code = -1
    path = request.REQUEST.get("path")
    auth = request.REQUEST.get("auth")
    realmd5 = md5hex("%s%s"%(path,PASSWD))
    if realmd5 == auth:
        if os.path.exists(path) :
            code=os.path.getsize(path)
        else :
            code=0;
    else :
        code=-2 #没有权限
        
    t = loader.get_template("response.html")
    c = Context({ 'result': code })
    return HttpResponse(t.render(c))

def deleteFile(request):
    """删除cdn源站上的文件"""
    code = 0
    path = request.REQUEST.get("path")
    auth = request.REQUEST.get("auth")
    realmd5 = md5hex("%s%s"%(path,PASSWD))
    global info 
    info = ""
    # 限制只能删除指定路径下的文件
    if (path.startswith("/repository/android_game_repository/new/game1/") == False) and (path.startswith("/usr/local/data_resource/android/new/game1/") == False):
        code=-2 #没有权限
        info = info + "删除失败,路径不正确"
    # md5权限限制
    elif realmd5 != auth:
        code=-2 #没有权限
        info = info + "删除失败,没有权限"
    if code !=-2 :
        if os.path.exists(path) and os.path.isfile(path) :
            #不直接删除,而是移动到其他目录,在适当的时候,手动删除
            currentMonth = "%s"%(datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m"))
            moveToPathSub="/new/need_delete/%s/"%currentMonth
            moveToPath=path.replace("/new/game1/", moveToPathSub)
            slashLastIndex=moveToPath.rfind("/")
            moveToFolder=moveToPath[0:slashLastIndex+1]
            if not os.path.exists(moveToFolder):
                os.makedirs(moveToFolder)
            os.rename(path, moveToPath)
            info = info + "删除成功"
        else :
            info = info + "删除失败，文件不存在"
            code=0;

    t = loader.get_template("response.html")
    c = Context({ 'result': info })
    return HttpResponse(t.render(c))


latestFlushTime=datetime.datetime.now()

def flushImgAndroidDCnCdn(request):
    """推送更新到cdn"""
    global latestFlushTime
    code = 0
    vendor = request.REQUEST.get("vendor")
    url = request.REQUEST.get("url")
    now =  datetime.datetime.now()
    info="刷新失败"
    timespan=now - latestFlushTime
    diff=timespan.total_seconds()
    
    if diff<30:
        info="刷新失败，操作太频繁"
        t = loader.get_template("response.html")
        c = Context({ 'result': info })
        return HttpResponse(t.render(c))
    else :
        if len(url.strip())<1:
            info="刷新失败，url不能为空"
        else :
            info=notifyDunionCDN(url)
        latestFlushTime=now
        t = loader.get_template("response.html")
        c = Context({ 'result': info })
        return HttpResponse(t.render(c))

#推送内容给帝联
def notifyDunionCDN(url):
    readCode=""
    try:
        data={}
        data['username']='imgpush'
        data['password']='cdn123!@#push'
        data['type']='1'
        data['url']=url.replace("\r\n", "")
        data['decode']='n'
        url="http://pushwt.dnion.com/cdnUrlPush.do"
        aa=urllib.urlencode(data)
        fp=urllib.urlopen(url,urllib.urlencode(data))
        readCode=fp.read()
        fp.close()
    except Exception,ex:
        readCode= "系统错误，操作失败，%s"%(ex)
    finally:
        return readCode.decode("GBK")


