#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2014/12/18 09:09:22 $"
###########################################
#ȫ��������վ��ͼ����
###########################################
import sys
import datetime
import StringIO
import traceback
import xml.etree.ElementTree as ElementTree
from djutil.DBUtil import DBUtil
from djutil.MailUtil import MailUtil
from djutil.OptsUtil import OptsUtil

#��ʼ������
dbUtil_35 = DBUtil('droid_game_10')
#�������
dbUtil_21 = DBUtil('djstore_21')

#�������²�������
ADD_OPERATE_TYPE = 1
DELETE_OPERATE_TYPE = 0

#վ��ĸ���Ƶ�ʺ����ȼ�
CHANGE_FREQ_DIC = {'indexPage':'daily', 'listPage':'weekly', 'detailPage':'monthly'}
PRIORITY_DIC = {'indexPage':'1.0', 'listPage':'0.3', 'detailPage':'0.6'}

#վ���ͼ���·��

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

#վ���ͼURL
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



#�ű�ִ��״̬�ļ�·��
RUNNING_STATUS_FILE = "/usr/local/bin/cdroid_business/buildSitemap_running_status.txt"
#RUNNING_STATUS_FILE = "E:/buildSitemap_running_status.txt"

#####�ʼ���������
ERROR_MSG = ""
mailServer = "mail.downjoy.com"
mailFromName = u"������������".encode("gbk")
mailFromAddr = "webmaster@downjoy.com"
mailLoginUser = "webmaster@downjoy.com"
mailLoginPass = "htbp3dQ1sGcco!q"
mailSubject = u"������վ��ͼ������Ϣ��buildSitemap.py��".encode("gbk")
mailTo = ['shan.liang@downjoy.com', 'lin.he@downjoy.com']
mailContents = u'Hi: \n'

#�����ʼ�
def sendMail():
    global mailContents
    mailContents = (mailContents + u'ִ�����ڣ�%s\n������Ϣ��%s\nлл��' % (datetime.datetime.today(), ERROR_MSG)).encode('gbk')
    mail = MailUtil(None, mailServer, mailFromName, mailFromAddr, mailTo, mailLoginUser, mailLoginPass, mailSubject)
    mail.sendMailMessage(mailContents)

#�����ҳ
def buildSitemapForGiftList(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})

    lastModifyDate = datetime.datetime.now()

    #���������ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage'])

    #����б�ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�����ȫ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��Ȩ���
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #���ֿ�
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #������
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/help.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #���ְ���
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�ҵ����
    #�����ȫҳ��
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��һҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_2.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�ڶ�ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_3.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_4.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/all_5.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����ҳ
    #��Ȩ����б�ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_3_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�Ժ�
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #Ԥ��
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_21_256_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�
    #���ֿ��б�ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_3_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�Ժ�
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #Ԥ��
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_20_256_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�
    #�������б�ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_3_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�Ժ�
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #Ԥ��
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/gift_list_22_256_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�
    #�ҵ�����б�ҳ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_1_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����ȡ
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_2_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��Ԥ��
    addOneWebSite(urlsetElm_Web, "http://mall.d.cn/list_myItem_4_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��ϲ��

    #Wap��ҳ
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage'])
    #WAP�����ȫ
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/list_netgame.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    #WAP�����ȫ
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/list_my_account.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
    #WAP��Ԥ���ĺ�
    addOneWapSite(urlsetElm_Wap, "http://sq.d.cn/mall/list_my_book.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])

#���浽�ļ�
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(GIFT_WEB_LIST_SITEMAP_PATH)
    siteMapTree_Wap.write(GIFT_WAP_LIST_SITEMAP_PATH)

#��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, GIFT_WEB_LIST_SITEMAP_URL)
    addOneSitemap(sitemapindexElm, GIFT_WAP_LIST_SITEMAP_URL)
#����������վ���ͼ(ȫ��)
def buildSitemapForGiftDetail(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    lastModifyDate = datetime.datetime.now()
#���е��������ҳ
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
        # ÿ4000�����ݴ�һ��xml�ļ�
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(GIFT_WEB_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(GIFT_WAP_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #��ӵ���׿�ٶȵ�ͼ��
            addOneSitemap(sitemapindexElm, GIFT_WEB_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, GIFT_WAP_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000))

        #��һҳ��ѯ
        startIdx = startIdx + limitRange

    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(GIFT_WEB_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(GIFT_WAP_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))

    #��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, GIFT_WEB_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, GIFT_WAP_DETAIL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))

#���е�������վ���ͼ(ȫ��)
def buildSitemapAllGift(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    lastModifyDate = datetime.datetime.now()
#�������
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
        # ÿ4000�����ݴ�һ��xml�ļ�
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(GIFT_WEB_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(GIFT_WAP_DETAIL_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #��ӵ���׿�ٶȵ�ͼ��
            addOneSitemap(sitemapindexElm, GIFT_WEB_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, GIFT_WAP_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000))

        #��һҳ��ѯ
        startIdx = startIdx + limitRange

    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(GIFT_WEB_CHANNEL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(GIFT_WAP_CHANNEL_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))

    #��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, GIFT_WEB_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, GIFT_WAP_CHANNEL_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))


#��Ϸ��������վ���ͼ(ȫ��)
def buildSitemapForGameSoftware(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    
    #������Ϸ�����
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
            if resourceType == 1: #��Ϸ
                siteUrl_Web = "http://android.d.cn/game/" + str(resourceId) + ".html"
                siteUrl_Wap = "http://a.d.cn/game/" + str(resourceId) + "/"
            else: #���
                siteUrl_Web = "http://android.d.cn/software/" + str(resourceId) + ".html"
                siteUrl_Wap = "http://a.d.cn/software/" + str(resourceId) + "/"
            #���Webվ�� 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            #���Wapվ�� 
            addOneWapSite(urlsetElm_Wap, siteUrl_Wap, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            
        # ÿ4000�����ݴ�һ��xml�ļ�
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(ANDROID_WEB_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(ANDROID_WAP_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #��ӵ���׿�ٶȵ�ͼ��
            addOneSitemap(sitemapindexElm, ANDROID_WEB_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, ANDROID_WAP_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            
        #��һҳ��ѯ
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(ANDROID_WAP_GAMESOFTWARE_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    
    #��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, ANDROID_WEB_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, ANDROID_WAP_GAMESOFTWARE_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    
#���Ի���Ѷ����ҳ���վ���ͼ(ȫ��)
def buildSitemapForIndnNews(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    
    #�������Ի���Ѷ
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
            if appType == 1:  #����Ӧ������Ϸ�����
                if newsType == 70: #����
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/gonglve/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/gonglve/" + str(newsId) + ".html"
                elif newsType == 71: #����
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/pingce/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/pingce/" + str(newsId) + ".html"
                elif newsType == 72: #��Ѷ
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/zixun/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/zixun/" + str(newsId) + ".html"
                elif newsType == 73: #�ʴ�
                    siteUrl_Web = "http://android.d.cn/game/" + str(appId) + "/wenda/" + str(newsId) + ".html"
                    siteUrl_Wap = "http://a.d.cn/game/" + str(appId) + "/wenda/" + str(newsId) + ".html"
                else:
                    continue
            else:
                continue
            #���Webվ�� 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            #���Wapվ�� 
            addOneWapSite(urlsetElm_Wap, siteUrl_Wap, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
        
        # ÿ4000�����ݴ�һ��xml�ļ�
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(ANDROID_WEB_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(ANDROID_WAP_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #��ӵ���׿�ٶȵ�ͼ��
            addOneSitemap(sitemapindexElm, ANDROID_WEB_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, ANDROID_WAP_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
        
        #��һҳ��ѯ
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(ANDROID_WAP_INDNNEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    
    #��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, ANDROID_WEB_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, ANDROID_WAP_INDNNEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))

#��Ѷ����ҳ���վ���ͼ(ȫ��)
def buildSitemapForNews(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
    
    #������Ѷ
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
            #���Webվ�� 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
            #���Wapվ�� 
            addOneWapSite(urlsetElm_Wap, siteUrl_Wap, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
        
        # ÿ4000�����ݴ�һ��xml�ļ�
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
            siteMapTree_Web.write(ANDROID_WEB_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            siteMapTree_Wap.write(ANDROID_WAP_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Wap.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})
            #��ӵ���׿�ٶȵ�ͼ��
            addOneSitemap(sitemapindexElm, ANDROID_WEB_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
            addOneSitemap(sitemapindexElm, ANDROID_WAP_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000))
        
        #��һҳ��ѯ
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    siteMapTree_Wap.write(ANDROID_WAP_NEWS_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    
    #��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, ANDROID_WEB_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    addOneSitemap(sitemapindexElm, ANDROID_WAP_NEWS_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    
#ר������ҳ���վ���ͼ(ȫ��)
def buildSitemapForSpecialtopic(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    
    #����ר��
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
            #���Webվ�� 
            addOneWebSite(urlsetElm_Web, siteUrl_Web, lastModifyDate, CHANGE_FREQ_DIC['detailPage'], PRIORITY_DIC['detailPage'])
        
        # ÿ4000�����ݴ�һ��xml�ļ�
        if (startIdx + limitRange) % 4000 == 0:
            siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
            siteMapTree_Web.write(ANDROID_WEB_SPECIALTOPICE_SITEMAP_PATH.format((startIdx + limitRange) / 4000))
            urlsetElm_Web.clear()
            urlsetElm_Web = ElementTree.Element("urlset")
            #��ӵ���׿�ٶȵ�ͼ��
            addOneSitemap(sitemapindexElm, ANDROID_WEB_SPECIALTOPICE_SITEMAP_URL.format((startIdx + limitRange) / 4000))
        
        #��һҳ��ѯ
        startIdx = startIdx + limitRange
        
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Web.write(ANDROID_WEB_SPECIALTOPICE_SITEMAP_PATH.format((startIdx + limitRange) / 4000 + 1))
    #��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, ANDROID_WEB_SPECIALTOPICE_SITEMAP_URL.format((startIdx + limitRange) / 4000 + 1))
    
#�б�ҳ���վ���ͼ(ȫ��)
def buildSitemapForList(sitemapindexElm):
    urlsetElm_Web = ElementTree.Element("urlset")
    urlsetElm_Wap = ElementTree.Element("urlset", {"xmlns:mobile":"http://www.baidu.com/schemas/sitemap-mobile/1/"})

    lastModifyDate = datetime.datetime.now()
    
    #Web��ҳ
    addOneWebSite(urlsetElm_Web, "http://android.d.cn", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage']) 
    
    #Web�б�ҳ
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��Ϸ�б�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����б�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�����б�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/news/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��Ѷ�б�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #ר���б�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/quan/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��ϷȦ�б�
    
    #Web��Ϸ�б�ҳ
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_1_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_15_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #��Ʒ
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_2_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_3_1_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_4_0_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_5_1_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #�ƽ�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_16_1_0_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/yugao/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����Ԥ��
    
    #Web����б�ҳ
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_1_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_2_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_4_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    
    #Web�����б�ҳ
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_1_0_0_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_2_0_0_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/netgame/list_4_0_0_0_0_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage']) #����
    
    #Web��������Ѷ�����б�ҳ���ų���������Ϸ����
    sql = 'SELECT ID, RESOURCE_TYPE FROM GAME_CATEGORY WHERE RESOURCE_TYPE in (1,2,3,7) AND ID != 17' 
    rows = dbUtil_35.queryList(sql)
    if rows:
        for row in rows:
            categoryId = row[0]
            resourceType = row[1]
            if resourceType == 1: #��Ϸ
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/game/list_1_0_" + str(categoryId) + "_0_0_0_0_0_0_0_0_1_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            elif resourceType == 2: #���
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/software/list_1_" + str(categoryId) + "_0.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            elif resourceType == 3: #��Ѷ
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/news/0/" + str(categoryId) + "/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            elif resourceType == 7: #ר��
                addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/0/" + str(categoryId) + "/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            else:
                continue

    #Webר�����������б�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/1/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#��Ƶ����
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/2/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#��Ϸ�ܿ�
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/3/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#�¶�ʮ��
    addOneWebSite(urlsetElm_Web, "http://android.d.cn/specialtopic/tag/0/4/", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])#����ܿ�
            
    #Web���η����б�ҳ
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
    
    #Wap��ҳ
    addOneWapSite(urlsetElm_Wap, "http://a.d.cn", lastModifyDate, CHANGE_FREQ_DIC['indexPage'], PRIORITY_DIC['indexPage']) 
    
    #Wap�б�ҳ
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
    
    #Wap�����б�ҳ
    sql = 'SELECT ID FROM GAME_CATEGORY WHERE RESOURCE_TYPE =1 AND ID != 17' 
    rows = dbUtil_35.queryList(sql)
    if rows:
        for row in rows:
            categoryId = row[0]
            addOneWapSite(urlsetElm_Wap, "http://a.d.cn/game/list_1_0_" + str(categoryId) + "_0_0_0_0_0_0_0_1.html", lastModifyDate, CHANGE_FREQ_DIC['listPage'], PRIORITY_DIC['listPage'])
            
    #���浽�ļ�
    siteMapTree_Web = ElementTree.ElementTree(urlsetElm_Web)
    siteMapTree_Wap = ElementTree.ElementTree(urlsetElm_Wap)
    siteMapTree_Web.write(ANDROID_WEB_LIST_SITEMAP_PATH)
    siteMapTree_Wap.write(ANDROID_WAP_LIST_SITEMAP_PATH)
    
    #��ӵ���׿�ٶȵ�ͼ��
    addOneSitemap(sitemapindexElm, ANDROID_WEB_LIST_SITEMAP_URL)
    addOneSitemap(sitemapindexElm, ANDROID_WAP_LIST_SITEMAP_URL)
 #author  shq




#���һ��WEBվ��
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
    
#���һ��WAPվ��
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

#ɾ�����վ��
def deleteSites(sitemapFilePath, waitDeleteSiteDic):
    if not waitDeleteSiteDic or len(waitDeleteSiteDic) == 0:
        return

    #������ɾ��
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

    #����
    if hasDeleteElm == True:
        siteMapTree.write(sitemapFilePath)

#���һ��sitemap
def addOneSitemap(sitemapindexElm, sitemapUrl):
    sitemapElm = ElementTree.SubElement(sitemapindexElm, "sitemap")
    locElm = ElementTree.SubElement(sitemapElm, "loc")
    lastmodElm = ElementTree.SubElement(sitemapElm, "lastmod")
    locElm.text = sitemapUrl
    lastmodElm.text = datetime.datetime.now().strftime("%Y-%m-%d")

#��׿ҵ��վ���ͼ
def buildSitemap_android():
    sitemapindexElm = ElementTree.Element("sitemapindex")

    buildSitemapForList(sitemapindexElm) #�б�ҳ���վ��
    buildSitemapForIndnNews(sitemapindexElm) #���Ի���Ѷ����ҳ���վ��
    buildSitemapForGameSoftware(sitemapindexElm) #��Ϸ���������ҳ���վ��
    buildSitemapForNews(sitemapindexElm) #��Ѷ����ҳ���վ��
    buildSitemapForSpecialtopic(sitemapindexElm) #ר������ҳ���վ��

    siteMapTree = ElementTree.ElementTree(sitemapindexElm)
    siteMapTree.write(ANDROID_SITEMAP_PATH)
#�����ͼ
def buildSitemap_gift():
     sitemapindexElm = ElementTree.Element("sitemapindex")
     buildSitemapForGiftList(sitemapindexElm) #����б�ҳ���վ��
     buildSitemapAllGift(sitemapindexElm)     #�������channel
     buildSitemapForGiftDetail(sitemapindexElm)   #�����������
     siteMapTree = ElementTree.ElementTree(sitemapindexElm)
     siteMapTree.write(GIFT_SITEMAP_PATH)

#www.d.cn��վ���ͼ  
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

#��������Ƿ������У���������У�ֱ�ӷ���true��
#���û�����У����ļ��м�¼�ı�ʶλ��Ϊtrue��ͬʱ����false
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
    
#�ű�ִ����ɺ���������״̬
def resetTaskStatus():
    f = file(RUNNING_STATUS_FILE, "w")
    f.write("false")
    f.close()
    
###############################################################
if __name__ == '__main__':
    try:
        #��¼��ʼʱ��
        startTime = datetime.datetime.now()
        
        #����
        taskRunning = checkTaskRunning()
        if taskRunning == False:
            #www.d.cn��վ���ͼ
            try:
                buildSitemap_wwwdcn()
            except Exception, ex:
                fp = StringIO.StringIO()    #�����ڴ��ļ�����
                traceback.print_exc(file = fp)
                ERROR_MSG = ERROR_MSG + str(fp.getvalue())

            #��׿վ���ͼ
            try:
                buildSitemap_android()
            except Exception, ex:
                fp = StringIO.StringIO()    #�����ڴ��ļ�����
                traceback.print_exc(file = fp)
                ERROR_MSG = ERROR_MSG + str(fp.getvalue())

            #���վ���ͼ
            try:
                buildSitemap_gift()
            except Exception, ex:
                fp = StringIO.StringIO()    #�����ڴ��ļ�����
                traceback.print_exc(file = fp)
                ERROR_MSG = ERROR_MSG + str(fp.getvalue())
                
        else :
            print "task already running,do nothing"
         
        #��¼�ܹ�����ʱ��
        spentTime = datetime.datetime.now() - startTime
        print spentTime
            
    except Exception, ex:
        fp = StringIO.StringIO()    #�����ڴ��ļ�����
        traceback.print_exc(file = fp)
        ERROR_MSG = str(fp.getvalue())
        raise Exception, ERROR_MSG

    finally:
        #��������״̬
        resetTaskStatus()
        if dbUtil_35: dbUtil_35.close()
        if ERROR_MSG:
           print ERROR_MSG
           sendMail()