#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "$Author: wuz $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2014/03/29 $"

###################################################################################################
##
## 微信推广链接
## 需要部署在WEB服务器所在服务器，采用http://android.d.cn/zt/weixin/index.html进行访问
## crontab配置：
## 0 5 * * *  /usr/local/bin/component/createWeixinPage.py >> /var/log/createWeixinPage.log 2>&1
##
###################################################################################################

import MySQLdb
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import traceback
import smtplib
import httplib
import json


#异常邮件接收者
MONITOR_MAIL=['zhou.wu@downjoy.com','shan.liang@downjoy.com']

#数据库连接
conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game", use_unicode=True, charset='utf8')
cursor = conn.cursor()

#web网站服务器IP:port
#IP_LIST = ['api.ios.d.cn']
IP_IOS = "api.ios.d.cn"

# 生成页面存放路径
PAGE_ADDS = "/usr/local/apache/htdocs/zt/weixin/index.html"
RESOURCE_PATH = "http://raw.android.d.cn/cdroid_res/weixin/resources20140402"

null=''

#发送邮件
def sendmail(From, To, msgBody, title):
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","htbp3dQ1sGcco!q")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(msgBody, 'html', 'gb2312')
    main_msg.attach(text_msg)

    main_msg['From'] = From
    main_msg['To'] = ', '.join(To)
    main_msg['Subject'] = title
    main_msg['Date'] = email.Utils.formatdate( )
    fullText = main_msg.as_string()
    try:
        server.sendmail(From, To, fullText)
    finally:
        server.quit()

# 获得Android端数据
def getTop20FormAndroid():
    resList = []
    # 单机游戏TOP10查询
    sql = ''' SELECT G.ID AS ID,
                     G.NAME AS NAME,
                     G.ICON AS ICON,
                     G.DOWNS AS CNT,
                     G.STARS AS STARS,
                     TRUNCATE(P.FILE_SIZE/1024/1024, 2) AS FILE_SIZE,
                     REPLACE(CONCAT(P.URL, '?f=digua_2'),
                       CASE
                          WHEN G.COPYRIGHT_TYPE = '0' THEN "http://c.downandroid.com/android/"
                          WHEN G.COPYRIGHT_TYPE = '1' THEN "http://res.d.cn/android/"
                          ELSE ""
                       END, PUP.PREFIX
                       ) AS URL
            FROM GAME G
            INNER JOIN DOWNLOAD_WEEKLY_GAME_TOP300 D ON D.GAME_ID = G.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            LEFT JOIN PUBLISH_URL_PREFIX PUP ON PUP.COPYRIGHT = G.COPYRIGHT_TYPE
            WHERE G.LINKS > 0
            AND G.STATUS = 1
            AND P.CHANNEL_FLAG_SET & 4 = 4
            AND P.SYNC_CHANNEL_FLAG_SET & 4 = 4
            AND G.RESOURCE_TYPE = 1
            AND P.IS_DEFAULT = 1
            AND PUP.CHANNEL_FLAG = 4
            AND PUP.STATUS = 1
            AND PUP.GROUP_NAME IN ('DIGUA_COPYRIGHT_NO', 'DIGUA_COPYRIGHT')
            GROUP BY G.ID
            ORDER BY D.CNT DESC
            LIMIT 10 '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    if not rows or (len(rows) == 0) or (not rows[0][0]):
        return resList
    for row in rows:
        resourceInfo = {}
        resourceInfo['ID'] = row[0]
        resourceInfo['NAME'] = row[1]
        resourceInfo['ICON'] = row[2]
        resourceInfo['CNT'] = row[3]
        resourceInfo['STARS'] = row[4]
        resourceInfo['FILE_SIZE'] = row[5]
        resourceInfo['URL'] = row[6]
        resList.append(resourceInfo);

    # 网游TOP10查询
    sql = '''SELECT NC.ID AS ID,
	    NC.NAME AS ID,
	    NC.HDICON AS ICON,
	    NC.DOWNS AS CNT,
	    NC.STARS AS STARS,
	    TRUNCATE(P.FILE_SIZE/1024/1024, 2) AS FILE_SIZE,
	    CONCAT(P.URL, '?f=digua_2') AS URL
        FROM NETGAME_DOWN_STAT NDS
        INNER JOIN NETGAME_CHANNEL NC ON NDS.WEEK_CHANNEL_ID = NC.ID
        LEFT JOIN NETGAME_GAME NG ON NC.ID = NG.CHANNEL_ID
        LEFT JOIN NETGAME_GAME_PKG P ON NG.ID = P.GAME_ID
        WHERE P.ID =
            (SELECT MAX(ID) FROM NETGAME_GAME_PKG P2 WHERE P2.GAME_ID=NG.ID AND P2.NETGAME_SYNC_STATUS > 0)
        GROUP BY NC.ID
        ORDER BY NC.DOWNS DESC
        LIMIT 10'''
    cursor.execute(sql)
    rows = cursor.fetchall()
    if not rows or (len(rows) == 0) or (not rows[0][0]):
        return resList
    for row in rows:
        resourceInfo = {}
        resourceInfo['ID'] = row[0]
        resourceInfo['NAME'] = row[1]
        resourceInfo['ICON'] = row[2]
        resourceInfo['CNT'] = row[3]
        resourceInfo['STARS'] = row[4]
        resourceInfo['FILE_SIZE'] = row[5]
        resourceInfo['URL'] = row[6]
        resList.append(resourceInfo);

    resList = sorted(resList, key = lambda x:x['CNT'], reverse = True)
    return resList


#调用IOS服务接口，从IOS服务获取排名前20的数据
def getTop20FormIOS():
    global null
    resList = []
    url = "/api/ranklistbyjson.ashx?platform=iphone&apptype=Games&ishd=1&Datetype=2&pagesize=20"
    conn = httplib.HTTPConnection(IP_IOS)
    conn.request("GET", url)
    res = conn.getresponse()
    data = eval(res.read())
    for i in range(0, len(data)):
        resourceInfo = {}
        obj = json.dumps(data[i], ensure_ascii=False)
        obj_dict = eval(obj)
        resourceInfo["ID"] = obj_dict['ID']
        resourceInfo["NAME"] = obj_dict['Name'].decode("utf8")
        resourceInfo["ICON"] = obj_dict['IconUrl'].decode("utf8")
        resourceInfo['CNT'] = obj_dict['DownloadCount']
        resourceInfo['STARS'] = obj_dict['AppStar']
        resourceInfo['FILE_SIZE'] = obj_dict['Size']
        resourceInfo['URL'] = obj_dict['PListUrl'] #可以在浏览器的下载地址
        resList.append(resourceInfo);

    # IOS提供的数据已经是周排行过后的顺序，不需要排序了。是周排行，显示总下载次数
    #resList = sorted(resList, key = lambda x:x['CNT'], reverse = True)
    return resList

def CNT(obj):
    return obj['CNT']

def tabHtml(tabId, dataList):
    headStr = u'''<ul class="cont" id="%s-cont">''' % (tabId)
    count = 1
    for list in dataList:
        tmp = u'''<li class="item">
                    <em>%s</em>
                        <img xSrc="%s" src="%s/img/holder.png" alt="%s" class="thumb"/>
                        <a href="%s" title="%s" class="btn">立即下载</a>
                        <div class="des">
                            <p class="tit">%s</p>
                            <p class="num">%s</p>
                            <p>
                                <span class="size">%s M</span>
                                <span class="star">
                                    <span class="star-inner star%s"></span>
                                </span>
                            </p>
                        </div>
                    </li>''' % (count, list['ICON'], RESOURCE_PATH, list['NAME'],
                                list['URL'], list['NAME'], list['NAME'],
                                getFileSize(list['CNT']), list['FILE_SIZE'], int(list['STARS']))
        headStr = headStr + tmp
        count = count+1
    headStr = headStr + '</ul>'
    return headStr

def getFileSize(size):
    size = float(size)
    sizeStr = u""
    if size > 10000:
        size=int(size/100)
        if size % 100 == 0:
            sizeStr = u'''%d万次下载''' % (size/100)
        else:
            sizeStr = u'''%-10.2f万次下载''' % (float(size)/100)
    else:
        sizeStr = u'''%d次下载''' % size

    return sizeStr

def makeHtml():
    htmlStr = u'''
    <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="utf-8"/>
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no"/>
        <meta name="format-detection"content="telephone=no">
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black" />
        <title>排行榜</title>
        <link href="%s/css/common.css" rel="stylesheet" type="text/css" />
    </head>
    <body>
    <div class="head">
        <h2 class="current" data-tab="android" id="android">安卓</h2>
        <h2 class="" data-tab="ios" id="ios">苹果</h2>
    </div>
    <div class="content">''' % RESOURCE_PATH

    alist = getTop20FormAndroid()
    aStr = tabHtml("android", alist);
    ilist = getTop20FormIOS();
    iStr = tabHtml("ios", ilist);
    htmlStr = htmlStr + aStr + iStr;
    htmlStr = htmlStr + u'''</div>
        <div class="mask" id="mask"></div>
        <div class="guide-cont" id="guide">
            <img src="%s/img/guide.png" alt=""/>
            <a href="javascript:;" class="close" id="close">知道了</a>
        </div>
        <div class="dpktip" id="dpktip">
            <p class="tip-detail">
                该应用为dpk格式，请到<br /><span>当乐游戏中心</span>下载!<br />
                打开浏览器-输入<br /><span>app.d.cn</span>一键安装-可以<br />玩啦！
            </p>
            <i id="closeDpk" class="close-dpk"></i>
        </div>
        <script type="text/javascript">
            function is_weixn(){
                var ua = navigator.userAgent.toLowerCase();
                if(ua.match(/MicroMessenger/i)=="micromessenger") {
                    return true;
                }
                return false;
            }
            var guide = (function(){
                var mask = document.getElementById("mask");
                if(!is_weixn()){
                    mask.style.display = "none";
                    mask.style.height = document.body.clientHeight + "px";
                    return;
                } else {
                    guideCont = document.getElementById("guide");
                    mask.style.height = document.body.clientHeight + "px";
                    guideCont.style.visibility = "visible";
                }
            })();
            var browser={
                versions:function(){
                    var u = navigator.userAgent;
                    return {
                        iPhone: u.indexOf('iPhone') > -1  //是否为iPhone或者QQHD浏览器
                    };
                }()
            };
        </script>
        <script src="%s/js/zepto.min.js" type="text/javascript"></script>
        <script src="%s/js/main.js" type="text/javascript"></script>
        </body>
        </html>''' % (RESOURCE_PATH, RESOURCE_PATH, RESOURCE_PATH)
    return htmlStr

def createHtml(htmlStr):
    f = file(PAGE_ADDS, "w")
    f.write(htmlStr)
    f.close()

###############################################################
if __name__ == '__main__':
    try:
        htmlStr = makeHtml()
        createHtml(htmlStr.encode("UTF-8"))
    except Exception, ex:
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, traceback.format_exc(), u"微信炫彩页面生成出错,118.144.66.139_usr_local_bin_component_createWeixinPage.py")
        print 'exception sendmail'
        raise Exception

    finally:
        cursor.close()
        conn.close()
