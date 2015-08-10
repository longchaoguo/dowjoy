#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2014/12/18 09:09:22 $"
###########################################
#全量更新网站地图数据
###########################################
import sys
import datetime
import StringIO
import traceback
import xml.etree.ElementTree as ElementTree
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

#初始化参数
dbUtil_35 = DBUtil('droid_game_10')
#礼包中心
dbUtil_21 = DBUtil('djstore_21')

#增量更新操作类型
ADD_OPERATE_TYPE = 1
DELETE_OPERATE_TYPE = 0

#站点的更新频率和优先级
CHANGE_FREQ_DIC = {'indexPage':'daily', 'listPage':'weekly', 'detailPage':'monthly'}
PRIORITY_DIC = {'indexPage':'1.0', 'listPage':'0.3', 'detailPage':'0.6'}

#站点地图存放路径

ANDROID_WEB_LIST_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/webListSitemap.xml'
ANDROID_WAP_LIST_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/wapListSitemap.xml'
ANDROID_WEB_INDNNEWS_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/webIndnnewsSitemap{0}.xml'
ANDROID_WAP_INDNNEWS_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/wapIndnnewsSitemap{0}.xml'
ANDROID_WEB_NEWS_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/webNewsSitemap{0}.xml'
ANDROID_WAP_NEWS_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/wapNewsSitemap{0}.xml'
ANDROID_WEB_SPECIALTOPICE_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/webSpecialtopicSitemap{0}.xml'
ANDROID_WEB_GAMESOFTWARE_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/webGameSoftwareSitemap{0}.xml'
ANDROID_WAP_GAMESOFTWARE_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap/wapGameSoftwareSitemap{0}.xml'
ANDROID_SITEMAP_PATH = '/usr/local/nfs/sitemap/andriodsitemap/sitemap.xml'
SITEMAP_PATH = '/usr/local/nfs/sitemap/wwwsitemap/sitemap/sitemap.xml'

GIFT_WEB_LIST_SITEMAP_PATH = '/usr/local/nfs/sitemap/mallsitemap/sitemap/webGiftListSitemap.xml'
GIFT_WAP_LIST_SITEMAP_PATH = '/usr/local/nfs/sitemap/mallsitemap/sitemap/wapGiftListSitemap.xml'
GIFT_WEB_CHANNEL_SITEMAP_PATH = '/usr/local/nfs/sitemap/mallsitemap/sitemap/webChannel{0}.xml'
GIFT_WAP_CHANNEL_SITEMAP_PATH = '/usr/local/nfs/sitemap/mallsitemap/sitemap/wapChannel{0}.xml'
GIFT_WEB_DETAIL_SITEMAP_PATH = '/usr/local/nfs/sitemap/mallsitemap/sitemap/webDetail{0}.xml'
GIFT_WAP_DETAIL_SITEMAP_PATH = '/usr/local/nfs/sitemap/mallsitemap/sitemap/wapDetail{0}.xml'
GIFT_SITEMAP_PATH = '/usr/local/nfs/sitemap/mallsitemap/sitemap.xml'


'''
ANDROID_WEB_LIST_SITEMAP_PATH = 'E:/sitemap/webListSitemap.xml'
ANDROID_WAP_LIST_SITEMAP_PATH = 'E:/sitemap/wapListSitemap.xml'
ANDROID_WEB_INDNNEWS_SITEMAP_PATH = 'E:/sitemap/webIndnnewsSitemap{0}.xml'
ANDROID_WAP_INDNNEWS_SITEMAP_PATH = 'E:/sitemap/wapIndnnewsSitemap{0}.xml'
ANDROID_WEB_NEWS_SITEMAP_PATH = 'E:/sitemap/webNewsSitemap{0}.xml'
ANDROID_WAP_NEWS_SITEMAP_PATH = 'E:/sitemap/wapNewsSitemap{0}.xml'
ANDROID_WEB_SPECIALTOPICE_SITEMAP_PATH = 'E:/sitemap/webSpecialtopicSitemap{0}.xml'
ANDROID_WEB_GAMESOFTWARE_SITEMAP_PATH = 'E:/sitemap/webGameSoftwareSitemap{0}.xml'
ANDROID_WAP_GAMESOFTWARE_SITEMAP_PATH = 'E:/sitemap/wapGameSoftwareSitemap{0}.xml'
ANDROID_SITEMAP_PATH = 'E:/sitemap/sitemap_android.xml'
SITEMAP_PATH = 'E:/sitemap/sitemap.xml'

GIFT_WEB_LIST_SITEMAP_PATH = 'E:/sitemap/webGiftListSitemap.xml'
GIFT_WAP_LIST_SITEMAP_PATH = 'E:/sitemap/wapGiftListSitemap.xml'
GIFT_WEB_CHANNEL_SITEMAP_PATH = 'E:/sitemap/webChannel{0}.xml'
GIFT_WAP_CHANNEL_SITEMAP_PATH = 'E:/sitemap/wapChannel{0}.xml'
GIFT_WEB_DETAIL_SITEMAP_PATH = 'E:/sitemap/webDetail{0}.xml'
GIFT_WAP_DETAIL_SITEMAP_PATH = 'E:/sitemap/wapDetail{0}.xml'
GIFT_SITEMAP_PATH = 'E:/sitemap.xml'
'''

#站点地图URL
ANDROID_WEB_LIST_SITEMAP_URL = 'http://android.d.cn/sitemap/webListSitemap.xml'
ANDROID_WAP_LIST_SITEMAP_URL = 'http://android.d.cn/sitemap/wapListSitemap.xml'
ANDROID_WEB_INDNNEWS_SITEMAP_URL = 'http://android.d.cn/sitemap/webIndnnewsSitemap{0}.xml'
ANDROID_WAP_INDNNEWS_SITEMAP_URL = 'http://android.d.cn/sitemap/wapIndnnewsSitemap{0}.xml'
ANDROID_WEB_NEWS_SITEMAP_URL = 'http://android.d.cn/sitemap/webNewsSitemap{0}.xml'
ANDROID_WAP_NEWS_SITEMAP_URL = 'http://android.d.cn/sitemap/wapNewsSitemap{0}.xml'
ANDROID_WEB_SPECIALTOPICE_SITEMAP_URL = 'http://android.d.cn/sitemap/webSpecialtopicSitemap{0}.xml'
ANDROID_WEB_GAMESOFTWARE_SITEMAP_URL = 'http://android.d.cn/sitemap/webGameSoftwareSitemap{0}.xml'
ANDROID_WAP_GAMESOFTWARE_SITEMAP_URL = 'http://android.d.cn/sitemap/wapGameSoftwareSitemap{0}.xml'

GIFT_WEB_LIST_SITEMAP_URL = 'http://mall.d.cn/sitemap/webGiftListSitemap.xml'
GIFT_WAP_LIST_SITEMAP_URL = 'http://mall.d.cn/sitemap/wapGiftListSitemap.xml'
GIFT_WEB_CHANNEL_SITEMAP_URL = 'http://mall.d.cn/sitemap/webChannel{0}.xml'
GIFT_WAP_CHANNEL_SITEMAP_URL = 'http://mall.d.cn/sitemap/wapChannel{0}.xml'
GIFT_WEB_DETAIL_SITEMAP_URL = 'http://mall.d.cn/sitemap/webDetail{0}.xml'
GIFT_WAP_DETAIL_SITEMAP_URL = 'http://mall.d.cn/sitemap/wapDetail{0}.xml'



#脚本执行状态文件路径
RUNNING_STATUS_FILE = "/usr/local/bin/cdroid_business/buildSitemap_running_status.txt"
#RUNNING_STATUS_FILE = "E:/buildSitemap_running_status.txt"

#####邮件报错提醒
ERROR_MSG = ""
mailServer = "mail.downjoy.com"
mailFromName = u"当乐数据中心".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"更新网站地图错误信息（buildSitemap.py）".encode("gbk")
mailTo = ['shan.liang@downjoy.com', 'lin.he@downjoy.com']
mailContents = u'Hi: \n'

#发送邮件
def sendMail():
    global mailContents
    mailContents = (mailContents + u'执行日期：%s\n错误信息：%s\n谢谢！' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

#礼包首页
def buildSitemapForGiftList(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})

    lastModifyDate = datetime.datetime.now()

    #礼包中心首页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage'])

    #礼包列表页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #礼包大全
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #特权礼包
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #新手卡
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #激活码
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/help.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #新手帮助
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #我的礼包
    #礼包大全页面
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #第一页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_2.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #第二页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_3.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #第三页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_4.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #第四页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_5.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #第五页
    #特权礼包列表页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #抢号
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_3_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #淘号
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #预订
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_256_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #活动
    #新手卡列表页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #抢号
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_3_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #淘号
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #预订
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_256_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #活动
    #激活码列表页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #抢号
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_3_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #淘号
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #预订
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_256_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #活动
    #我的礼包列表页
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #已领取
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #已预订
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_4_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #我喜欢

    #Wap首页
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage'])
    #WAP礼包大全
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/list_netgame.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    #WAP礼包大全
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/list_my_account.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    #WAP我预定的号
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/list_my_book.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])

#保存到文件
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(GIFT_WEB_LIST_SITEMAP_PATH)
    siteMapTree_Wap.write(GIFT_WAP_LIST_SITEMAP_PATH)

#添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, GIFT_WEB_LIST_SITEMAP_URL)
    addOneSitemap(sitemapindexElm, GIFT_WAP_LIST_SITEMAP_URL)
#礼包详情相关站点地图(全量)
def buildSitemapForGiftDetail(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    lastModifyDate = datetime.datetime.now()
#所有的礼包详情页
    sql ='select  S.ID  as ID  from SALE_SETTING S inner join ITEM I on S.ITEM_ID = I.ID  where 1=1 and (I.EXPIRE_DATE >now() or I.EXPIRE_DATE is null)   and I.STATUS = 1 and S.STATUS = 1  limit %d ,%d '
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_21.queryList(curSql)
        if not rows or len(rows) == 0:
            break
        for row in rows:
            saleID = row[0]
            addOneWebSite(urlsetElm_Web, "http://mall.d.cn/detail_" + str(saleID)+".html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/detail_"+str(saleID)+".html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
        # 每4000条数据存一个xml文件
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(GIFT_WEB_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(GIFT_WAP_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #添加到安卓百度地图中
            addOneSitemap(sitemapindexElm, GIFT_WEB_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, GIFT_WAP_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000))

        #下一页查询
        startIdx = startIdx + limitRange

    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(GIFT_WEB_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(GIFT_WAP_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))

    #添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, GIFT_WEB_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, GIFT_WAP_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))

#所有的礼包相关站点地图(全量)
def buildSitemapAllGift(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    lastModifyDate = datetime.datetime.now()
#所有礼包
    sql = 'SELECT  DISTINCT it.NETGAME_CHANNEL_ID  as channelID from  ITEM  it  where  it.NETGAME_CHANNEL_ID >0 limit %d, %d'
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_21.queryList(curSql)
        if not rows or len(rows) == 0:
            break
        for row in rows:
            saleID = row[0]
            addOneWebSite(urlsetElm_Web, "http://mall.d.cn/detail_" + str(saleID)+".html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/detail_"+str(saleID)+".html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/public.html?id="+str(saleID)+".html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
        # 每4000条数据存一个xml文件
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(GIFT_WEB_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(GIFT_WAP_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #添加到安卓百度地图中
            addOneSitemap(sitemapindexElm, GIFT_WEB_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, GIFT_WAP_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000))

        #下一页查询
        startIdx = startIdx + limitRange

    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(GIFT_WEB_CHANNEL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(GIFT_WAP_CHANNEL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))

    #添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, GIFT_WEB_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, GIFT_WAP_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))


#游戏、软件相关站点地图(全量)
def buildSitemapForGameSoftware(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    
    #遍历游戏、软件
    sql = 'select ID, RESOURCE_TYPE, LAST_MODIFY_DATE from GAME where STATUS = 1 and CHANNEL_ID = ID order by ID desc limit %d, %d'
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows or len(rows) == 0:
            break
        for row in rows:
            resourceId = row[0]
            resourceType = row[1]
            lastModifyDate = row[2]
            if resourceType == 1: #游戏
                siteUrl_Web = "http://android.d.cn/game/" + str(resourceId) + ".html"
                siteUrl_Wap = "http://a.d.cn/game/" + str(resourceId) + "/"
            else: #软件
                siteUrl_Web = "http://android.d.cn/software/" + str(resourceId) + ".html"
                siteUrl_Wap = "http://a.d.cn/software/" + str(resourceId) + "/"
            #添加Web站点 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            #添加Wap站点 
            addOneWapSite(urlsetElm_Wap, siteUrl_Wap, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            
        # 每4000条数据存一个xml文件
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(ANDROID_WEB_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(ANDROID_WAP_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #添加到安卓百度地图中
            addOneSitemap(sitemapindexElm, ANDROID_WEB_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, ANDROID_WAP_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            
        #下一页查询
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(ANDROID_WAP_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    
    #添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, ANDROID_WEB_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, ANDROID_WAP_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    
#个性化资讯详情页相关站点地图(全量)
def buildSitemapForIndnNews(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    
    #遍历个性化资讯
    sql = 'SELECT ID, GAME_CATEGORY_ID, LAST_MODIFY_DATE, APP_ID, APP_TYPE FROM INDN_NEWS where STATUS = 1 AND ORIGINAL_URL IS NULL order by ID desc limit %d, %d'
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows or len(rows) == 0:
            break
        for row in rows:
            newsId = row[0]
            newsType = row[1]
            lastModifyDate = row[2]
            appId = row[3]
            appType = row[4]
            if appType == 1:  #关联应用是游戏的情况
                if newsType == 70: #攻略
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/gonglve/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/gonglve/" + str(newsId) + ".html"
                elif newsType == 71: #评测
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/pingce/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/pingce/" + str(newsId) + ".html"
                elif newsType == 72: #资讯
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/zixun/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/zixun/" + str(newsId) + ".html"
                elif newsType == 73: #问答
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/wenda/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/wenda/" + str(newsId) + ".html"
                else:
                    continue
            else:
                continue
            #添加Web站点 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            #添加Wap站点 
            addOneWapSite(urlsetElm_Wap, siteUrl_Wap, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
        
        # 每4000条数据存一个xml文件
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(ANDROID_WEB_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(ANDROID_WAP_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #添加到安卓百度地图中
            addOneSitemap(sitemapindexElm, ANDROID_WEB_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, ANDROID_WAP_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
        
        #下一页查询
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(ANDROID_WAP_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    
    #添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, ANDROID_WEB_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, ANDROID_WAP_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))

#资讯详情页相关站点地图(全量)
def buildSitemapForNews(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    
    #遍历资讯
    sql = 'SELECT N.ID, N.LAST_MODIFY_DATE FROM NEWS N WHERE N.STATUS = 1 AND N.ORIGINAL_URL IS NULL AND N.GAME_CATEGORY_ID != 68 AND N.GAME_CATEGORY_ID != 69 ORDER BY N.ID DESC limit %d, %d'
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows or len(rows) == 0:
            break
        for row in rows:
            newsId = row[0]
            lastModifyDate = row[1]
            siteUrl_Web = "http://android.d.cn/news/" + str(newsId) + ".html"
            siteUrl_Wap = "http://a.d.cn/news/" + str(newsId) + ".html"
            #添加Web站点 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            #添加Wap站点 
            addOneWapSite(urlsetElm_Wap, siteUrl_Wap, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
        
        # 每4000条数据存一个xml文件
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(ANDROID_WEB_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(ANDROID_WAP_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #添加到安卓百度地图中
            addOneSitemap(sitemapindexElm, ANDROID_WEB_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, ANDROID_WAP_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
        
        #下一页查询
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(ANDROID_WAP_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    
    #添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, ANDROID_WEB_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, ANDROID_WAP_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    
#专题详情页相关站点地图(全量)
def buildSitemapForSpecialtopic(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    
    #遍历专题
    sql = 'SELECT T.ID, T.LAST_MODIFY_DATE FROM SPECIAL_TOPIC T WHERE T.STATUS = 1 AND T.ORIGINAL_URL IS NULL ORDER BY T.ID DESC limit %d, %d'
    startIdx = 0
    limitRange = 200
    while True:
        curSql = sql % (startIdx, limitRange)
        rows = dbUtil_35.queryList(curSql)
        if not rows or len(rows) == 0:
            break
        for row in rows:
            specialtopicId = row[0]
            lastModifyDate = row[1]
            siteUrl_Web = "http://android.d.cn/specialtopic/" + str(specialtopicId) + ".html"
            #添加Web站点 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
        
        # 每4000条数据存一个xml文件
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Web.write(ANDROID_WEB_SPECIALTOPICE_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            #添加到安卓百度地图中
            addOneSitemap(sitemapindexElm, ANDROID_WEB_SPECIALTOPICE_SITEMAP_URL.format((startIdx + limitRange) / 4000))
        
        #下一页查询
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Web.write(ANDROID_WEB_SPECIALTOPICE_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    #添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, ANDROID_WEB_SPECIALTOPICE_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    
#列表页相关站点地图(全量)
def buildSitemapForList(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})

    lastModifyDate = datetime.datetime.now()
    
    #Web首页
    addOneWebSite(urlsetElm_Web, "http://android.d.cn", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage']) 
    
    #Web列表页
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #游戏列表
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #软件列表
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #网游列表
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/news/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #资讯列表
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #专题列表
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/quan/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #游戏圈列表
    
    #Web游戏列表页
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_1_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #最新
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_15_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #新品
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_2_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #最热
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_3_1_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #大型
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_4_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #五星
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_5_1_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #破解
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_16_1_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #汉化
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/yugao/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #新游预告
    
    #Web软件列表页
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_1_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #最新
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_2_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #最热
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_4_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #五星
    
    #Web网游列表页
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_1_0_0_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #最新
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_2_0_0_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #最热
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_4_0_0_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #五星
    
    #Web单机、资讯分类列表页（排除‘其它游戏’）
    sql = 'SELECT ID, RESOURCE_TYPE FROM GAME_CATEGORY WHERE RESOURCE_TYPE in (1,2,3,7) AND ID != 17' 
    rows = dbUtil_35.queryList(sql)
    if rows:
        for row in rows:
            categoryId = row[0]
            resourceType = row[1]
            if resourceType == 1: #游戏
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_1_0_" + str(categoryId) + "_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            elif resourceType == 2: #软件
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_1_" + str(categoryId) + "_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            elif resourceType == 3: #资讯
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/news/0/" + str(categoryId) + "/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            elif resourceType == 7: #专题
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/0/" + str(categoryId) + "/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            else:
                continue

    #Web专题其它分类列表
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/1/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#视频播报
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/2/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#游戏周刊
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/3/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#月度十佳
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/4/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#软件周刊
            
    #Web网游分类列表页
    sql = 'SELECT ID, TYPE FROM NETGAME_CHANNEL_TAG WHERE NETGAME_SYNC_STATUS = 1' 
    rows = dbUtil_35.queryList(sql)
    if rows:
        for row in rows:
            categoryId = row[0]
            categoryType = row[1]
            if categoryType == 1:
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_1_" + str(categoryId) + "_0_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            else:
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_1_0_" + str(categoryId) + "_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    
    #Wap首页
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage']) 
    
    #Wap列表页
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_1_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_15_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_2_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_3_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_4_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_5_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_16_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_6_0_0_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/software/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) 
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/software/list_2_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/software/list_4_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/netgame/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/netgame/list_2_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/netgame/list_4_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/news/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/news/c-35/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/news/c-37/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn/news/c-36/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    
    #Wap分类列表页
    sql = 'SELECT ID FROM GAME_CATEGORY WHERE RESOURCE_TYPE =1 AND ID != 17' 
    rows = dbUtil_35.queryList(sql)
    if rows:
        for row in rows:
            categoryId = row[0]
            addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_1_0_" + str(categoryId) + "_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            
    #保存到文件
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_LIST_SITEMAP_PATH)
    siteMapTree_Wap.write(ANDROID_WAP_LIST_SITEMAP_PATH)
    
    #添加到安卓百度地图中
    addOneSitemap(sitemapindexElm, ANDROID_WEB_LIST_SITEMAP_URL)
    addOneSitemap(sitemapindexElm, ANDROID_WAP_LIST_SITEMAP_URL)
 #author  shq




#添加一个WEB站点
def addOneWebSite(urlsetElm, siteUrl, lastModifyDate, changefreq, priority, insertPos = -1):
    urlElm = ElementTree.Element("url")
    
    locElm = ElementTree.SubElement(urlElm, "loc")
    lastmodElm = ElementTree.SubElement(urlElm, "lastmod")
    changefreqElm = ElementTree.SubElement(urlElm, "changefreq")
    priorityElm = ElementTree.SubElement(urlElm, "priority")
    
    locElm.text = siteUrl
    if lastModifyDate:
        lastmodElm.text = lastModifyDate.strftime("%Y-%m-%d")
    else:
        lastmodElm.text = datetime.datetime.now().strftime("%Y-%m-%d")
    changefreqElm.text = changefreq
    priorityElm.text = priority
    
    if insertPos == -1:
        urlsetElm.append(urlElm)
    else:
        urlsetElm.insert(insertPos, urlElm)
    
#添加一个WAP站点
def addOneWapSite(urlsetElm, siteUrl, lastModifyDate, changefreq, priority, insertPos = -1):
    urlElm = ElementTree.Element("url")
    
    locElm = ElementTree.SubElement(urlElm, "loc")
    lastmodElm = ElementTree.SubElement(urlElm, "lastmod")
    changefreqElm = ElementTree.SubElement(urlElm, "changefreq")
    priorityElm = ElementTree.SubElement(urlElm, "priority")
    mobileElm = ElementTree.SubElement(urlElm, "mobile:mobile")
    
    locElm.text = siteUrl
    if lastModifyDate:
        lastmodElm.text = lastModifyDate.strftime("%Y-%m-%d")
    else:
        lastmodElm.text = datetime.datetime.now().strftime("%Y-%m-%d")
    changefreqElm.text = changefreq
    priorityElm.text = priority
    mobileElm.set("type", "mobile")
    
    if insertPos == -1:
        urlsetElm.append(urlElm)
    else:
        urlsetElm.insert(insertPos, urlElm)

#删除多个站点
def deleteSites(sitemapFilePath, waitDeleteSiteDic):
    if not waitDeleteSiteDic or len(waitDeleteSiteDic) == 0:
        return

    #遍历，删除
    hasDeleteElm = False
    siteMapTree = ElementTree.parse(sitemapFilePath)
    urlsetElm = siteMapTree.getroot()
    urlNodes = urlsetElm.getiterator("url")
    for urlNode in urlNodes:
        siteUrl = urlNode.findtext("loc")
        if waitDeleteSiteDic.has_key(siteUrl):
            modifyDateText = urlNode.findtext("lastmod")
            modifyDate = datetime.datetime.strptime(modifyDateText, '%Y-%m-%d')
            if modifyDate < waitDeleteSiteDic[siteUrl]:
                urlsetElm.remove(urlNode)
                hasDeleteElm = True

    #保存
    if hasDeleteElm == True:
        siteMapTree.write(sitemapFilePath)

#添加一个sitemap
def addOneSitemap(sitemapindexElm, sitemapUrl):
    sitemapElm = ElementTree.SubElement(sitemapindexElm, "sitemap")
    locElm = ElementTree.SubElement(sitemapElm, "loc")
    lastmodElm = ElementTree.SubElement(sitemapElm, "lastmod")
    locElm.text = sitemapUrl
    lastmodElm.text = datetime.datetime.now().strftime("%Y-%m-%d")

#安卓业务站点地图
def buildSitemap_android():
    sitemapindexElm = ElementTree.Element("sitemapindex")

    buildSitemapForList(sitemapindexElm) #列表页相关站点
    buildSitemapForIndnNews(sitemapindexElm) #个性化资讯详情页相关站点
    buildSitemapForGameSoftware(sitemapindexElm) #游戏、软件详情页相关站点
    buildSitemapForNews(sitemapindexElm) #资讯详情页相关站点
    buildSitemapForSpecialtopic(sitemapindexElm) #专题详情页相关站点

    siteMapTree = ElementTree.ElementTree(sitemapindexElm)
    siteMapTree.write(ANDROID_SITEMAP_PATH)
#礼包地图
def buildSitemap_gift():
     sitemapindexElm = ElementTree.Element("sitemapindex")
     buildSitemapForGiftList(sitemapindexElm) #礼包列表页相关站点
     buildSitemapAllGift(sitemapindexElm)     #所有礼包channel
     buildSitemapForGiftDetail(sitemapindexElm)   #所有礼包详情
     siteMapTree = ElementTree.ElementTree(sitemapindexElm)
     siteMapTree.write(GIFT_SITEMAP_PATH)

#www.d.cn总站点地图  
def buildSitemap_wwwdcn():
    sitemapindexElm = ElementTree.Element("sitemapindex")
    
    sitemapElm = ElementTree.SubElement(sitemapindexElm, "sitemap")
    locElm = ElementTree.SubElement(sitemapElm, "loc")
    lastmodElm = ElementTree.SubElement(sitemapElm, "lastmod")
    locElm.text = 'http://news.d.cn/sitemap.xml'
    lastmodElm.text = datetime.datetime.now().strftime("%Y-%m-%d")
    
    sitemapElm = ElementTree.SubElement(sitemapindexElm, "sitemap")
    locElm = ElementTree.SubElement(sitemapElm, "loc")
    lastmodElm = ElementTree.SubElement(sitemapElm, "lastmod")
    locElm.text = 'http://android.d.cn/sitemap.xml'
    lastmodElm.text = datetime.datetime.now().strftime("%Y-%m-%d")
    
    sitemapElm = ElementTree.SubElement(sitemapindexElm, "sitemap")
    locElm = ElementTree.SubElement(sitemapElm, "loc")
    lastmodElm = ElementTree.SubElement(sitemapElm, "lastmod")
    locElm.text = 'http://ng.d.cn/sitemap.xml'
    lastmodElm.text = datetime.datetime.now().strftime("%Y-%m-%d")

    siteMapTree = ElementTree.ElementTree(sitemapindexElm)
    siteMapTree.write(SITEMAP_PATH)

#检查任务是否在运行，如果在运行，直接返回true；
#如果没有运行，将文件中记录的标识位置为true，同时返回false
def checkTaskRunning():
    f = file(RUNNING_STATUS_FILE, "r")
    line = f.readline()
    f.close()
    if "true" == line:
        return True
    else :
        f = file(RUNNING_STATUS_FILE, "w")
        f.write("true")
        f.close()
        return False
    
#脚本执行完成后，重置运行状态
def resetTaskStatus():
    f = file(RUNNING_STATUS_FILE, "w")
    f.write("false")
    f.close()
    
###############################################################
if __name__ == '__main__':
    try:
        #记录开始时间
        startTime = datetime.datetime.now()
        
        #运行
        taskRunning = checkTaskRunning()
        if taskRunning == False:
            #www.d.cn总站点地图
            try:
                buildSitemap_wwwdcn()
            except Exception, ex:
                fp = StringIO.StringIO()    #创建内存文件对象
                traceback.print_exc(file = fp)
                ERROR_MSG = ERROR_MSG + str(fp.getvalue())

            #安卓站点地图
            try:
                buildSitemap_android()
            except Exception, ex:
                fp = StringIO.StringIO()    #创建内存文件对象
                traceback.print_exc(file = fp)
                ERROR_MSG = ERROR_MSG + str(fp.getvalue())

            #礼包站点地图
            try:
                buildSitemap_gift()
            except Exception, ex:
                fp = StringIO.StringIO()    #创建内存文件对象
                traceback.print_exc(file = fp)
                ERROR_MSG = ERROR_MSG + str(fp.getvalue())
                
        else :
            print "task already running,do nothing"
         
        #记录总共花销时间
        spentTime = datetime.datetime.now() - startTime
        print spentTime
            
    except Exception, ex:
        fp = StringIO.StringIO()    #创建内存文件对象
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        raise Exception, ERROR_MSG

    finally:
        #重置运行状态
        resetTaskStatus()
        if dbUtil_35: dbUtil_35.close()
        if ERROR_MSG:
           print ERROR_MSG
           sendMail()