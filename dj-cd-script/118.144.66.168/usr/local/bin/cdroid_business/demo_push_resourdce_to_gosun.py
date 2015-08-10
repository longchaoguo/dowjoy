#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
手动向高升推送更新
'''
import traceback
from datetime import *
import urllib,urllib2
import httplib
import json
import hashlib


class HttpTool(object):
    """
    Http工具类，封装常规Http操作
    """

    @staticmethod
    def get_str_md5(src):
        '''
        获取字符串的MD5值
        Args :
            src   : 待计算MD5字符串
        '''
        m0=hashlib.md5()
        m0.update(src)
        return m0.hexdigest()

    @staticmethod
    def url_escape(url):
        """
        url 特殊字符处理
        """
        eurl=url.replace(' ','%20')
        return eurl

    @staticmethod
    def post_data_by_body(host,url,data={},headers={},port=80,timeout=12000):
        """
        通过http post方式提交数据

        Args :
            host    : 服务器地址(必填)
            url     : post请求地址.
            data    : post参数(类型:dict) 
            timeout : 超时时间，单位毫秒
            header  : 

        Returns :
            请求内容
        """
        try:
            data_json = json.dumps(data)
            conn = httplib.HTTPConnection(host,port=port,timeout=timeout)
            conn.request(method="POST",url=url,body=data_json,headers=headers)
            response = conn.getresponse()
            return response.status,response.read()
        except Exception,e:
            return 500,traceback.format_exc()

    @staticmethod
    def post_data_by_form(host,url,data={},port=80,header={},timeout=12000):
        '''
        通过HTTP post表单方式提交数据

        Args:
            host    :   服务地地址(必填)
            url     :   post请求地址
            data    :   post参数
            timeout :   超时时间，单位毫秒

        Returns:
            状态码,返回内容
        '''
        try:
            form_params = urllib.urlencode(data)
            print "http://%s:%s%s"%(host,port,url)
            print form_params
            response = urllib2.urlopen("http://%s:%s%s?%s"%(host,port,url,form_params))
            return response.getcode(),response.read()
        except Exception,e:
            return 500,traceback.format_exc()


    @staticmethod
    def add_deliver_task(tasklist):
        '''
        '''
        if len(tasklist)>0:
            first_url = tasklist[0].get("url")
            digest = HttpTool.get_str_md5("11dangle123@#!%s"%(first_url))
            content_dict = {"userid":"11","digest":digest,"urls":tasklist}
            return HttpTool.post_data_by_body("gsvc.v.c4hcdn.com","/portal/mds/deliver_v2.jsp",data=content_dict,port=8080)

if __name__ == "__main__":
    tasklist = []
    urlList=[]
    urlList.append('http://g2.androidgame-store.com/android/new/game1/50/84850/modernaircombatonline_1434020960321.dpk')
    urlList.append('http://g2.androidgame-store.com/android/new/game1/99/93399/rj_1434332905496.apk')
    urlList.append('http://g2.androidgame-store.com/android/new/game1/66/96966/8wfgzpgf_1431324441677.apk')
    for url in urlList:
        task_item={}
        task_item["url"]=url
        task_item["itemid"]=HttpTool.get_str_md5(url)
        task_item["action"]="delete"
        tasklist.append(task_item)

    
    print HttpTool.add_deliver_task(tasklist)
