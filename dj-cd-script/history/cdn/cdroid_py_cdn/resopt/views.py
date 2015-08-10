#!/usr/bin/python
# -*- #coding:UTF-8
__author__ = "$Author: helin $"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/07/11 16:51:57 $"

from django.template import loader, Context
from django.http import HttpResponse
import hashlib
import os

PASSWD = ""

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
    if realmd5 == auth:
        if os.path.exists(path) and os.path.isfile(path) :
            code=os.remove(path)
        else :
            code=0;
    else :
        code=-2 #没有权限
        
    info="删除失败"
    if code == -2 :
        info="删除失败，没有权限"
    elif code == 0 :
        info="删除失败，文件不存在"
    else :
        info="删除成功"
    t = loader.get_template("response.html")
    c = Context({ 'result': info })
    return HttpResponse(t.render(c))


