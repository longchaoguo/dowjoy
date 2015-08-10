#!/usr/bin/python
# -*- #coding:cp936
from __builtin__ import str

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2013/11/21 $"

import sys
import MySQLdb
import traceback
import datetime
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import smtplib
import httplib

#异常邮件接收者
MONITOR_MAIL=['jiang.liu@downjoy.com']

#数据库连接
conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game", use_unicode=True, charset='utf8')
cursor = conn.cursor()

#标识不同排序列表
GAME_HOTEST_LIST = 1            #游戏最热列表
SOFTWARE_HOTEST_LIST = 2        #软件最热列表
NETGAME_HOTEST_LIST = 3         #网游最热列表
GAME_FIVESTAR_LIST = 4          #游戏五星列表
SOFTWARE_FIVESTAR_LIST = 5      #软件五星列表
NETGAME_FIVESTAR_LIST = 6       #网游五星列表
GAME_NEWEST_LIST = 7            #游戏最新列表
SOFTWARE_NEWEST_LIST = 8        #软件最新列表
NETGAME_NEWEST_LIST = 9         #网游最新列表
GAME_ORIGINAL_LIST = 9999       #游戏原始列表
SOFTWARE_ORIGINAL_LIST = 9998   #软件原始列表
NETGAME_ORIGINAL_LIST = 9997    #网游原始列表
TYPE_DIC = {GAME_HOTEST_LIST:'GAME_HOTEST_LIST', GAME_FIVESTAR_LIST:'GAME_5STARS_LIST', GAME_NEWEST_LIST:'GAME_NEWEST_LIST', GAME_ORIGINAL_LIST:'GAME_ORIGINAL_LIST', SOFTWARE_HOTEST_LIST:'SOFTWARE_HOTEST_LIST', SOFTWARE_FIVESTAR_LIST:'SOFTWARE_5STARS_LIST', SOFTWARE_NEWEST_LIST:'SOFTWARE_NEWEST_LIST', SOFTWARE_ORIGINAL_LIST:'SOFTWARE_ORIGINAL_LIST', NETGAME_HOTEST_LIST:'NETGAME_HOTEST_LIST', NETGAME_FIVESTAR_LIST:'NETGAME_5STARS_LIST', NETGAME_NEWEST_LIST:'NETGAME_NEWEST_LIST', NETGAME_ORIGINAL_LIST:'NETGAME_ORIGINAL_LIST'}

#标识不同资源类别
RESOURCE_TYPE_GAME = 1      #游戏
RESOURCE_TYPE_SOFTWARE = 2  #软件
RESOURCE_TYPE_NETGAME = 5   #网游

#标识不同排序列表的资源类型（resource_type）
LIST_RESOURCE_TYPE_DIC = {GAME_HOTEST_LIST:RESOURCE_TYPE_GAME, GAME_FIVESTAR_LIST:RESOURCE_TYPE_GAME, GAME_NEWEST_LIST:RESOURCE_TYPE_GAME, GAME_ORIGINAL_LIST:RESOURCE_TYPE_GAME, SOFTWARE_HOTEST_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_FIVESTAR_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_NEWEST_LIST:RESOURCE_TYPE_SOFTWARE, SOFTWARE_ORIGINAL_LIST:RESOURCE_TYPE_SOFTWARE, NETGAME_HOTEST_LIST:RESOURCE_TYPE_NETGAME, NETGAME_FIVESTAR_LIST:RESOURCE_TYPE_NETGAME, NETGAME_NEWEST_LIST:RESOURCE_TYPE_NETGAME, NETGAME_ORIGINAL_LIST:RESOURCE_TYPE_NETGAME}

#不需要插入广告位的列表
NOT_ADVERTISE_LIST = [GAME_ORIGINAL_LIST, SOFTWARE_ORIGINAL_LIST, NETGAME_ORIGINAL_LIST]

#地瓜服务器IP:port
DIGUA_IP_LIST = ['192.168.0.211:7011', '192.168.0.155:7011', '192.168.0.167:7011', '192.168.0.174:7011']

#全局变量
TAG_DIC = {} #标签
ORG_GAME_LIST = [] #原始游戏列表
ORG_SOFTWARE_LIST = [] #原始软件列表
ORG_NETGAME_LIST = [] #原始网游列表

class Entry(object):
    def __init__(self, val, p= None):
        self.data = val
        self.next = p

    # 每次append都是在链表头的位置添加
    def append(self, value):
        prevous = Entry(self.data)
        self.data = value;
        self.next = prevous
    
    def gettail(self):
        p = self
        while p and p.next:
            p = self.next
        return p    

    def tolist(self):
        result = []
        if(self.data):
            result.append(self.data)
        p = self.next
        while p:
            if p.data:
                result.append(p.data)
            p = p.next
        
        return result

#发送邮件
def sendmail(From, To, msgBody, title):
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","bourne@8.3")
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

#调用web服务接口，清理web服务的二级缓存中的列表状态信息
def cleanListTableStatusCache():
    #清除digua缓存
    for ip in DIGUA_IP_LIST:
        url = "/clean/ablist"
        conn = httplib.HTTPConnection(ip)
        conn.request("GET", url)
        res = conn.getresponse()
        data = res.read()

	#清除newdigua列表缓存
    url = "/newdiguaserver/clean/redis/cleankeyprefix?key=_new_digua_game_newest_list_language"
    conn = httplib.HTTPConnection("api2014.digua.d.cn")
    conn.request("GET", url)
    data = res.read()

    return
    
#初始化标签信息
def initTag():
    global TAG_DIC
    sql = '''SELECT T.ID, T.NAME FROM CLIENT_TAG T WHERE T.STATUS = 1'''
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows and (len(rows) > 0) and rows[0][0]:
        for row in rows:
            TAG_DIC[row[1]] = row[0]
            
#获取游戏列表信息（按publishDate排序）
def initOrgGameList():
    global ORG_GAME_LIST
    sql = '''SELECT G.ID,
                    G.NAME,
                    G.EN_NAME,
                    G.GAME_CATEGORY_ID,
                    G.COMMENTS,
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT,
                    G.STARS,
                    G.ICON,
                    G.LATEST_VERSION_NAME,
                    G.DATA_TYPE,
                    G.LANGUAGE_TYPE,
                    G.PUBLISH_DATE,
                    G.CREATED_DATE AS G_CREATED_DATE,
                    G.GOOD_RATING_CNT,
                    C.NAME AS CNAME,
                    G.BANNER,
                    P.FILE_SIZE,
                    MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                    BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                    MIN(P.MIN_SDK) AS MIN_SDK,
                    BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                    G.COPYRIGHT_TYPE,
                    G.SCORE,
                    G.DOWNS,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.IMAGE_410X250,
                    P.URL,
                    G.CHANNEL_ID,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TIP_TYPE, 
                    G.COLLECT_CNT, 
                    G.TAGS,
                    G.STATUS,
                    G.VENDOR_ID 
            FROM GAME G
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.RESOURCE_TYPE = 1
            AND G.STATUS = 1
            AND P.STATUS = 1
            GROUP BY G.ID
            ORDER BY G.PUBLISH_DATE DESC 
            limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    allRows = []
    
    while True:
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(sql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum
            
    if (not allRows) or (len(allRows) == 0) or (not allRows[0][0]):
        return
    for row in allRows:
        #将如果DIGUA、WEB、WAP渠道都没有同步好的游戏过滤出去（1：WEB  2: WAP  4：DIGUA）
        if row[18] & 1 == 0 and row[18] & 2 == 0 and row[18] & 4 == 0:
            continue
        channelTO = ChannelTO()
        channelTO.setId(row[0])
        channelTO.setName(row[1])
        channelTO.setEnName(row[2])
        channelTO.setCategoryId(row[3])
        channelTO.setComments(row[4])
        channelTO.setHotCnt(row[5])
        channelTO.setStars(row[6])
        channelTO.setIcon(row[7])
        channelTO.setLastestVerName(row[8])
        channelTO.setDataType(row[9])
        channelTO.setLanguageType(row[10])
        channelTO.setPublishDate(row[11])
        channelTO.setCreatedDate(row[12])
        channelTO.setGoodRatingCnt(row[13])
        channelTO.setCategoryName(row[14])
        channelTO.setBanner(row[15])
        channelTO.setPkgFileSize(row[16])
        channelTO.setPkgCreatedDate(row[17])
        channelTO.setPkgChannelFlagSet(row[18])
        channelTO.setMinSdk(row[19])
        channelTO.setSreenSizeSet(row[20])
        channelTO.setCopyrightType(row[21])
        channelTO.setScore(row[22])
        channelTO.setDowns(row[23])
        channelTO.setOutline(row[24])
        channelTO.setDescription(row[25])
        channelTO.setImage_410X250(row[26])
        channelTO.setUrl(row[27])
        channelTO.setChannelId(row[28])
        channelTO.setCategoryTabFlagSet(row[29])
        channelTO.setTipType(row[30])
        if row[31]:
            channelTO.setCollectCnt(row[31])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setTagIds(getTagIdsByNames(row[32]))
        channelTO.setStatus(row[33])
        channelTO.setVendorId(row[34])
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        channelTO.setResourceType(1)
        channelTO.setAdvLanguageType(0)
        
        ORG_GAME_LIST.append(channelTO)
#获取软件信息（按publishDate排序）
def initOrgSoftwareList():
    global ORG_SOFTWARE_LIST
    sql = '''SELECT G.ID,
                    G.NAME,
                    G.EN_NAME,
                    G.GAME_CATEGORY_ID,
                    G.COMMENTS,
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT,
                    G.STARS,
                    G.ICON,
                    G.LATEST_VERSION_NAME,
                    G.DATA_TYPE,
                    G.LANGUAGE_TYPE,
                    G.PUBLISH_DATE,
                    G.CREATED_DATE AS G_CREATED_DATE,
                    G.GOOD_RATING_CNT,
                    C.NAME AS CNAME,
                    G.BANNER,
                    P.FILE_SIZE,
                    MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                    BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                    MIN(P.MIN_SDK) AS MIN_SDK,
                    BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                    G.COPYRIGHT_TYPE,
                    G.SCORE,
                    G.DOWNS,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.IMAGE_410X250,
                    P.URL,
                    G.CHANNEL_ID,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TIP_TYPE, 
                    G.COLLECT_CNT, 
                    G.TAGS,
                    G.STATUS,
                    G.VENDOR_ID 
            FROM GAME G
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.RESOURCE_TYPE = 2
            AND G.STATUS = 1
            AND P.STATUS = 1
            GROUP BY G.ID
            ORDER BY G.PUBLISH_DATE DESC 
            limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    allRows = []

    while True:
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(sql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum
             
    if (not allRows) or (len(allRows) == 0) or (not allRows[0][0]):
        return
    for row in allRows:
        #将DIGUA、WEB、WAP渠道都没有同步好的游戏过滤出去（1：WEB  2: WAP  4：DIGUA）
        if row[18] & 1 == 0 and row[18] & 2 == 0 and row[18] & 4 == 0:
            continue
        channelTO = ChannelTO()
        channelTO.setId(row[0])
        channelTO.setName(row[1])
        channelTO.setEnName(row[2])
        channelTO.setCategoryId(row[3])
        channelTO.setComments(row[4])
        channelTO.setHotCnt(row[5])
        channelTO.setStars(row[6])
        channelTO.setIcon(row[7])
        channelTO.setLastestVerName(row[8])
        channelTO.setDataType(row[9])
        channelTO.setLanguageType(row[10])
        channelTO.setPublishDate(row[11])
        channelTO.setCreatedDate(row[12])
        channelTO.setGoodRatingCnt(row[13])
        channelTO.setCategoryName(row[14])
        channelTO.setBanner(row[15])
        channelTO.setPkgFileSize(row[16])
        channelTO.setPkgCreatedDate(row[17])
        channelTO.setPkgChannelFlagSet(row[18])
        channelTO.setMinSdk(row[19])
        channelTO.setSreenSizeSet(row[20])
        channelTO.setCopyrightType(row[21])
        channelTO.setScore(row[22])
        channelTO.setDowns(row[23])
        channelTO.setOutline(row[24])
        channelTO.setDescription(row[25])
        channelTO.setImage_410X250(row[26])
        channelTO.setUrl(row[27])
        channelTO.setChannelId(row[28])
        channelTO.setCategoryTabFlagSet(row[29])
        channelTO.setTipType(row[30])
        if row[31]:
            channelTO.setCollectCnt(row[31])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setTagIds(getTagIdsByNames(row[32]))
        channelTO.setStatus(row[33])
        channelTO.setVendorId(row[34])
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        channelTO.setResourceType(2)
        
        ORG_SOFTWARE_LIST.append(channelTO)
        
#获取网游信息
def initOrgNetgameList():
    global ORG_NETGAME_LIST
    sql = '''select C.ID,
                    C.NAME,
                    C.PINYIN,
                    C.HDICON,
                    C.TAG_NAMES,
                    C.STARS,
                    C.HOT_CNT,
                    C.CREATED_DATE,
                    C.LAST_UPDATE_DATE,
                    G.LAST_VERSION_NUM,
                    GP.FILE_SIZE,
                    C.BANNER,
                    MIN(GPM.MIN_SDK),
                    BIT_OR(GPM.SCREEN_SIZE_SET),
                    C.TAG_IDS,
                    C.SCORE,
                    C.DOWNS,
                    CASE
                        WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                        ELSE C.OUTLET_LINE
                    END AS OUTLINE,
                    C.DESCRIPTION,
                    MAX(GP.CREATED_DATE), 
                    C.COLLECT_CNT,
                    C.OPERATION_STATUS,
                    C.CP_ID 
            from NETGAME_CHANNEL C
            left join NETGAME_GAME G ON C.ID = G.CHANNEL_ID
            left join NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
            left join NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
            where C.NETGAME_SYNC_STATUS > 0 
            and C.STATUS = 1
            and (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS > 0)
            and (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS > 0)
            group by C.ID
            order by C.LAST_UPDATE_DATE desc
            limit %s, %s'''
    startIdx = 0
    pageNum = 1000
    allRows = []
    
    while True:
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(sql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum
            
    if (not allRows) or (len(allRows) == 0) or (not allRows[0][0]):
        return
    for row in allRows:
        channelTO = ChannelTO()
        channelTO.setId(row[0])
        channelTO.setChannelId(row[0])
        channelTO.setName(row[1])
        channelTO.setPinyin(row[2])
        channelTO.setIcon(row[3])
        channelTO.setCategoryName(row[4])
        channelTO.setStars(row[5])
        channelTO.setHotCnt(row[6])
        channelTO.setCreatedDate(row[7])
        channelTO.setPublishDate(row[8])
        channelTO.setLastestVerName(row[9])
        channelTO.setPkgFileSize(row[10])
        channelTO.setBanner(row[11])
        channelTO.setMinSdk(row[12])
        channelTO.setSreenSizeSet(row[13])
        channelTO.setCategoryId(row[14])
        channelTO.setScore(row[15])
        channelTO.setDowns(row[16])
        channelTO.setOutline(row[17])
        channelTO.setDescription(row[18])
        channelTO.setPkgCreatedDate(row[19])
        if row[20]:
            channelTO.setCollectCnt(row[20])
        else:
            channelTO.setCollectCnt(0)
        channelTO.setStatus(row[21])
        channelTO.setVendorId(row[22])
        channelTO.setDataType(0)
        channelTO.setLanguageType(7) #网游默认为支持中-2、英-1、韩-4
        channelTO.setResourceType(5)
        channelTO.setTipType(0)
        channelTO.setPkgChannelFlagSet(511)
        channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
        channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
        ORG_NETGAME_LIST.append(channelTO)

#转换标签名称到标签ID
def getTagIdsByNames(tagNames):
    if not tagNames:
        return None
        
    tagIds = ''
    tagNameArr = tagNames.strip().split(',')
    for tagName in tagNameArr:
        if tagName in TAG_DIC:
            tagId = TAG_DIC[tagName]
            tagIds = tagIds + ',' + str(tagId)
    
    if len(tagIds) > 0:
        tagIds = tagIds + ','
        
    return tagIds
    
#获取包大小范围
def getFileSizeScope(fileSize):
    if fileSize <= 50 * 1024 * 1024:
        return 1
    elif fileSize <= 100 * 1024 * 1024:
        return 2
    elif fileSize <= 300 * 1024 * 1024:
        return 3
    elif fileSize <= 500 * 1024 * 1024:
        return 4
    elif fileSize <= 1024 * 1024 * 1024:
        return 5
    else:
        return 6
        
#获取上线年份
def getOnlineYear(createdDate):
    sysYear = datetime.date.today().year
    onlineYear = createdDate.year
    if onlineYear <= sysYear - 4: #如果为当年倒退4年之后，则设为-1，表示‘更早’
        onlineYear = -1
    else:
        onlineYear = sysYear - onlineYear + 1
    
    return onlineYear
  
#获取数据库中的列表状态信息
def getTableName(sortType):
    tableName = ''
    type = TYPE_DIC[sortType]
    sql = "select TABLE_NAME from GAME_LIST_TABLE_STATUS where TYPE = '%s'" % type
    cursor.execute(sql)
    rows = cursor.fetchall()

    if not rows or (len(rows) == 0) or (not rows[0][0]):
        return tableName
    else:
        tableName = rows[0][0]

    return tableName

#获得资源信息详细信息
def getResourceInfo(channelId, resourceType):
    channelTO = None
    if (resourceType == RESOURCE_TYPE_GAME) or (resourceType == RESOURCE_TYPE_SOFTWARE):
        sql = '''SELECT G.ID,
                    G.NAME,
                    G.EN_NAME,
                    G.GAME_CATEGORY_ID,
                    G.COMMENTS,
                    COALESCE(ROUND(LEAST(LOG(1.1, G.HOT_CNT), 100)),0) AS HOT_CNT,
                    G.STARS,
                    G.ICON,
                    G.LATEST_VERSION_NAME,
                    G.DATA_TYPE,
                    G.LANGUAGE_TYPE,
                    G.PUBLISH_DATE,
                    G.CREATED_DATE AS G_CREATED_DATE,
                    G.GOOD_RATING_CNT,
                    C.NAME AS CNAME,
                    G.BANNER,
                    P.FILE_SIZE,
                    MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                    BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                    MIN(P.MIN_SDK) AS MIN_SDK,
                    BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                    G.COPYRIGHT_TYPE,
                    G.SCORE,
                    G.DOWNS,
                    G.OUTLINE,
                    G.DESCRIPTION,
                    G.IMAGE_410X250,
                    P.URL,
                    G.CHANNEL_ID,
                    G.GAME_CATEGORY_TAB_FLAG_SET,
                    G.TIP_TYPE, 
                    G.COLLECT_CNT, 
                    G.TAGS,
                    G.STATUS,
                    G.VENDOR_ID 
            FROM GAME G 
            INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
            INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
            WHERE G.ID = %d
            AND G.RESOURCE_TYPE = %d
            AND G.STATUS = 1
            AND P.STATUS = 1''' % (channelId, resourceType)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows and (len(rows) > 0) and rows[0][0]:
            #如果DIGUA、WEB、WAP渠道都没有同步好,过滤出去（1：WEB  2: WAP  4：DIGUA）
            row = rows[0]
            if row[18] & 1 == 0 and row[18] & 2 == 0 and row[18] & 4 == 0:
                return None
            channelTO = ChannelTO()
            channelTO.setId(row[0])
            channelTO.setName(row[1])
            channelTO.setEnName(row[2])
            channelTO.setCategoryId(row[3])
            channelTO.setComments(row[4])
            channelTO.setHotCnt(row[5])
            channelTO.setStars(row[6])
            channelTO.setIcon(row[7])
            channelTO.setLastestVerName(row[8])
            channelTO.setDataType(row[9] | 16) #16表示该资源是一个广告位，用于前台角标的展示
            channelTO.setLanguageType(row[10])
            channelTO.setPublishDate(row[11])
            channelTO.setCreatedDate(row[12])
            channelTO.setGoodRatingCnt(row[13])
            channelTO.setCategoryName(row[14])
            channelTO.setBanner(row[15])
            channelTO.setPkgFileSize(row[16])
            channelTO.setPkgCreatedDate(row[17])
            channelTO.setPkgChannelFlagSet(row[18])
            channelTO.setMinSdk(row[19])
            channelTO.setSreenSizeSet(row[20])
            channelTO.setCopyrightType(row[21])
            channelTO.setScore(row[22])
            channelTO.setDowns(row[23])
            channelTO.setOutline(row[24])
            channelTO.setDescription(row[25])
            channelTO.setImage_410X250(row[26])
            channelTO.setUrl(row[27])
            channelTO.setChannelId(row[28])
            channelTO.setCategoryTabFlagSet(row[29])
            channelTO.setTipType(row[30])
            if row[31]:
                channelTO.setCollectCnt(row[31])
            else:
                channelTO.setCollectCnt(0)
            channelTO.setTagIds(getTagIdsByNames(row[32]))
            channelTO.setStatus(row[33])
            channelTO.setVendorId(row[34])
            channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
            channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
            channelTO.setResourceType(resourceType)
               
    elif resourceType == RESOURCE_TYPE_NETGAME:
        sql = '''select C.ID,
                        C.NAME,
                        C.PINYIN,
                        C.HDICON,
                        C.TAG_NAMES,
                        C.STARS,
                        C.HOT_CNT,
                        C.CREATED_DATE,
                        C.LAST_UPDATE_DATE,
                        G.LAST_VERSION_NUM,
                        GP.FILE_SIZE,
                        C.BANNER,
                        MIN(GPM.MIN_SDK),
                        BIT_OR(GPM.SCREEN_SIZE_SET),
                        C.TAG_IDS,
                        C.SCORE,
                        C.DOWNS,
                        CASE
                            WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                            ELSE C.OUTLET_LINE
                        END AS OUTLINE,
                        C.DESCRIPTION,
                        MAX(GP.CREATED_DATE), 
                        C.COLLECT_CNT,
                        C.OPERATION_STATUS,
                        C.CP_ID 
                FROM NETGAME_CHANNEL C
                LEFT JOIN NETGAME_GAME G ON C.ID = G.CHANNEL_ID
                LEFT JOIN NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
                LEFT JOIN NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
                WHERE C.ID = %d
                AND C.NETGAME_SYNC_STATUS > 0
                AND C.STATUS = 1
                AND (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS > 0)
                AND (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS > 0)''' % channelId
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows and (len(rows) > 0) and rows[0][0]:
            channelTO = ChannelTO()
            row = rows[0]
            channelTO.setId(row[0])
            channelTO.setChannelId(row[0])
            channelTO.setName(row[1])
            channelTO.setPinyin(row[2])
            channelTO.setIcon(row[3])
            channelTO.setCategoryName(row[4])
            channelTO.setStars(row[5])
            channelTO.setHotCnt(row[6])
            channelTO.setCreatedDate(row[7])
            channelTO.setPublishDate(row[8])
            channelTO.setLastestVerName(row[9])
            channelTO.setPkgFileSize(row[10])
            channelTO.setBanner(row[11])
            channelTO.setMinSdk(row[12])
            channelTO.setSreenSizeSet(row[13])
#             channelTO.setCategoryId(row[14])
            channelTO.setScore(row[15])
            channelTO.setDowns(row[16])
            channelTO.setOutline(row[17])
            channelTO.setDescription(row[18])
            channelTO.setPkgCreatedDate(row[19])
            if row[20]:
                channelTO.setCollectCnt(row[20])
            else:
                channelTO.setCollectCnt(0)
            channelTO.setStatus(row[21])
            channelTO.setVendorId(row[22])
            channelTO.setDataType(16) #16表示该资源是一个广告位，用于前台角标的展示
            channelTO.setLanguageType(7) #网游默认为支持中-2、英-1、韩-4
            channelTO.setResourceType(5)
            channelTO.setTipType(0)
            channelTO.setPkgChannelFlagSet(511)
            channelTO.setPkgFileSizeScope(getFileSizeScope(channelTO.getPkgFileSize()))
            channelTO.setOnlineYear(getOnlineYear(channelTO.getCreatedDate()))
            
    return channelTO

#获得运营自定义的在列表页中的资源（游戏/软件/网游）排序信息
def reOrderSortList(sortType, sortList, languageType):
    sql = '''SELECT RESOURCE_ID,
                    RESOURCE_TYPE,
                    POSITION
             FROM GAME_LIST_CUSTOM_ADV
             WHERE LIST_TYPE = %d
             AND LANGUAGE_TYPE = %d
             ORDER BY POSITION ASC''' % (sortType, languageType)
    cursor.execute(sql)
    rows = cursor.fetchall()

    exclusion_ids = ''
    if not rows: 
        return exclusion_ids
    count = 0
    for row in rows:
        position = int(row[2])
        # 业务规则：网游列表中只能插入网游广告位，游戏/软件过滤掉
        if (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_NETGAME) and (row[1] != RESOURCE_TYPE_NETGAME):
#             print "netgame resource list not allow insert the non netgame resource, custom resource:%d, language_type:%d"   %(row[0], languageType)
            continue

        #获取广告位资源信息
        customResourceInfo = getResourceInfo(row[0], row[1])
        if not customResourceInfo:
#             print "resource not found, ignore custom resource, custom resource:%d, language_type:%d"   %(row[0], languageType)
            continue
        
        if GAME_FIVESTAR_LIST == sortType and customResourceInfo.getStars() != 5:
            continue
        # 设置广告位语言类型
        customResourceInfo.setAdvLanguageType(languageType)
        tmpChannelTO = None
        tmpEntry = None
        index = position - 1
        if position > 0 and position < len(sortList):
            tmpEntry = sortList[index]
            tmpChannelTO = tmpEntry.data
            if not tmpChannelTO:
                continue
            if tmpChannelTO.getAdvLanguageType() == 0: # 如果该节点的值为
                sortList.insert(index, Entry(customResourceInfo))
            else:
                tmpEntry.append(customResourceInfo)
            
            if LIST_RESOURCE_TYPE_DIC[sortType] ==  customResourceInfo.getResourceType():
                exclusion_ids = exclusion_ids + ',' + str(customResourceInfo.getId())
            count += 1
        
    print 'list reorder success, original len: %d, sortcount: %d, languageType :%d' % (len(rows), count, languageType)

    return exclusion_ids

#获得游戏原始排序的列表(exclusion_ids:由于已经是广告位，需要排除的ID)
def getOriginalGameSortList(sortType, isEntry):
    orgSortList = []
    if sortType == GAME_HOTEST_LIST:  #最热
        for channelTO in ORG_GAME_LIST:
            if isEntry:
              orgSortList.append(Entry(channelTO))
            else:
              orgSortList.append(channelTO)
        if isEntry:
            orgSortList = sorted(orgSortList, key=lambda entry: entry.data.hotCnt, reverse=True)
        else:
            orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == GAME_NEWEST_LIST or sortType == GAME_ORIGINAL_LIST:
        for channelTO in ORG_GAME_LIST:
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
        return orgSortList
    elif sortType == GAME_FIVESTAR_LIST: #五星
        for channelTO in ORG_GAME_LIST:
            if channelTO.getStars() != 5:
                continue
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
    return orgSortList
    
 #获得软件原始排序的列表
def getOriginalSoftwareSortList(sortType, isEntry):
    orgSortList = []
    if sortType == SOFTWARE_HOTEST_LIST:  #最热
        for channelTO in ORG_SOFTWARE_LIST:
            if (isEntry):
              orgSortList.append(Entry(channelTO))
            else:
              orgSortList.append(channelTO)
        if isEntry:
            orgSortList = sorted(orgSortList, key=lambda entry: entry.data.hotCnt, reverse=True)
        else:
            orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == SOFTWARE_NEWEST_LIST or sortType == SOFTWARE_ORIGINAL_LIST:
        for channelTO in ORG_SOFTWARE_LIST:
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
        return orgSortList
    elif sortType == SOFTWARE_FIVESTAR_LIST: #五星
        for channelTO in ORG_SOFTWARE_LIST:
            if channelTO.getStars() != 5:
                continue
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
    return orgSortList

#获得网游原始排序的列表
def getOriginalNetgameSortList(sortType, isEntry):
    orgSortList = []
    if sortType == NETGAME_HOTEST_LIST:  #最热
        for channelTO in ORG_NETGAME_LIST:
            if (isEntry):
              orgSortList.append(Entry(channelTO))
            else:
              orgSortList.append(channelTO)
        if isEntry:
            orgSortList = sorted(orgSortList, key=lambda entry: entry.data.hotCnt, reverse=True)
        else:
            orgSortList = sorted(orgSortList, key=lambda channelTO: channelTO.hotCnt, reverse=True)
    elif sortType == NETGAME_NEWEST_LIST or sortType == NETGAME_ORIGINAL_LIST:
        for channelTO in ORG_NETGAME_LIST:
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
        return orgSortList
    elif sortType == NETGAME_FIVESTAR_LIST: #五星
        for channelTO in ORG_NETGAME_LIST:
            if channelTO.getStars() != 5:
                continue
            if (isEntry):
                orgSortList.append(Entry(channelTO))
            else:
                orgSortList.append(channelTO)
    return orgSortList
#===============================================================================
# 获得有广告位插入、排序后的列表
# 1.需要非常注意的一点是，如果是advLanguaged 为True，也就是表明有区分语言了的，则需要简体中文，繁体中文一并查
# 2.如果没有advLanguaged则只差一次
#===============================================================================
def getAdvertiseSortList(sortType, advLanguaged = False):
    
    sortList = getOriginalSortList(sortType, True)
    # 运营自定义排序
    exclusion_ids = ','
    if(advLanguaged):
        exclusion_ids += reOrderSortList(sortType, sortList, 2)  # 简体中文
        exclusion_ids += reOrderSortList(sortType, sortList, 32)  # 繁体中文
    else:
        exclusion_ids += reOrderSortList(sortType, sortList, 2)

    resultlist = []
    orginalChannelEntry = None
    # sortList
    for entry in sortList:
        orginalChannelEntry = entry.gettail()
        if (not orginalChannelEntry) or (not orginalChannelEntry.data):
            continue
        # 如果需要剔除掉的id中找到对应的id,则将entry的这个一位的数据置空,tolist不会读出来，则去掉了
        if (orginalChannelEntry.data.getAdvLanguageType() == 0 and exclusion_ids.find(str(orginalChannelEntry.data.getId())) != -1):
            orginalChannelEntry.data = None
        for data in entry.tolist():
            resultlist.append(data)
           
    print 'get sort list, original len%d, final rows len: %d' % (len(sortList), len(resultlist))
    return resultlist

#获取原始排序列表
def getOriginalSortList(sortType, isEntry = False):
    originalSortList = []
    
    #如果是游戏类型的排序，则从原始的游戏列表中剔除
    if LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_GAME:
        originalSortList = getOriginalGameSortList(sortType, isEntry)
    #如果是软件类型的排序，则从原始的软件列表中剔除
    elif LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_SOFTWARE:
        originalSortList = getOriginalSoftwareSortList(sortType, isEntry)
    #否则从原始的网游中剔除
    else:
        originalSortList = getOriginalNetgameSortList(sortType, isEntry)
    print 'orignal rows len: %d' % (len(originalSortList))

    return originalSortList

#获得最终排序好的列表
def getSortList(sortType, advLanguaged = False):
    if sortType in NOT_ADVERTISE_LIST:
        return getOriginalSortList(sortType)
    else:
        return getAdvertiseSortList(sortType, advLanguaged)

#获取待操作的表名
def getTableNameForInsert(sortType):
    tableName = getTableName(sortType)
    print tableName

    if tableName[-1] == 'A':
        tableName = tableName[:-1] + 'B'
    elif tableName[-1] == 'B':
        tableName = tableName[:-1] + 'A'
    else:
        tableName = ''

    return tableName

#清空待操作表
def clearTable(tableName):
    sql = ''
    sql = "TRUNCATE TABLE %s" % tableName
    cursor.execute(sql)
    conn.commit()

#===============================================================================
# #插入排序后的列表信息
# advLanguaged 是否需要插入广告位语言类型， 需要注意，目前只需要对游戏的几张表做语言同步，所以增加这个参数
#===============================================================================
def insertResourceInfos(tableName, sortList, advLanguaged):
    sql = ''
    seq = 1
    if not sortList: 
        return
    datalist = []
    
    if(advLanguaged):
        for channelTO in sortList:
            sql = "INSERT INTO %s " % tableName
            sql += "(ID, RESOURCE_ID, NAME, ENNAME, PINYIN, CATEGORY_ID, CATEGORY_NAME, CATEGORY_TAB_FLAG_SET, RESOURCE_TYPE, COMMENT, HOT_CNT, STARS, RESOURCE_PUBLISH_DATE, ICON, BANNER, COPYRIGHT_TYPE, GOOD_RATING_CNT, FILE_SIZE, SCREEN_SIZE_SET, MIN_SDK, LATEST_VERSION_NAME, CREATED_DATE, PKG_CREATED_DATE, DATA_TYPE, LANGUAGE_TYPE, PKG_CHANNEL_FLAG_SET, SCORE, DOWNS, OUTLINE, DESCRIPTION, IMAGE_410X250, URL, TIP_TYPE, COLLECT_CNT, PKG_FILE_SIZE_SCOPE, ONLINE_YEAR, TAG_IDS, STATUS, VENDOR_ID, CHANNEL_ID, ADV_LANGUAGE_TYPE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            datalist.append((seq,
                             channelTO.getId(),
                             channelTO.getName(),
                             channelTO.getEnName(),
                             channelTO.getPinyin(),
                             channelTO.getCategoryId(),
                             channelTO.getCategoryName(),
                             channelTO.getCategoryTabFlagSet(),
                             channelTO.getResourceType(),
                             channelTO.getComments(),
                             channelTO.getHotCnt(),
                             channelTO.getStars(),
                             channelTO.getPublishDate(),
                             channelTO.getIcon(),
                             channelTO.getBanner(),
                             channelTO.getCopyrightType(),
                             channelTO.getGoodRatingCnt(),
                             channelTO.getPkgFileSize(),
                             channelTO.getSreenSizeSet(),
                             channelTO.getMinSdk(),
                             channelTO.getLastestVerName(),
                             channelTO.getCreatedDate(),
                             channelTO.getPkgCreatedDate(),
                             channelTO.getDataType(),
                             channelTO.getLanguageType(),
                             channelTO.getPkgChannelFlagSet(),
                             channelTO.getScore(),
                             channelTO.getDowns(),
                             channelTO.getOutline(),
                             channelTO.getDescription(),
                             channelTO.getImage_410X250(),
                             channelTO.getUrl(),
                             channelTO.getTipType(),
                             channelTO.getCollectCnt(),
                             channelTO.getPkgFileSizeScope(),
                             channelTO.getOnlineYear(),
                             channelTO.getTagIds(),
                             channelTO.getStatus(),
                             channelTO.getVendorId(),
                             channelTO.getChannelId(),
                             channelTO.getAdvLanguageType()))
            seq += 1
            if len(datalist)>=1000:
                cursor.executemany(sql, tuple(datalist))
                conn.commit()
                datalist = []
                
        if datalist:
            cursor.executemany(sql, tuple(datalist))
            conn.commit()
            datalist = []                
    else:
        for channelTO in sortList:
            sql = "INSERT INTO %s " % tableName
            sql += "(ID, RESOURCE_ID, NAME, ENNAME, PINYIN, CATEGORY_ID, CATEGORY_NAME, CATEGORY_TAB_FLAG_SET, RESOURCE_TYPE, COMMENT, HOT_CNT, STARS, RESOURCE_PUBLISH_DATE, ICON, BANNER, COPYRIGHT_TYPE, GOOD_RATING_CNT, FILE_SIZE, SCREEN_SIZE_SET, MIN_SDK, LATEST_VERSION_NAME, CREATED_DATE, PKG_CREATED_DATE, DATA_TYPE, LANGUAGE_TYPE, PKG_CHANNEL_FLAG_SET, SCORE, DOWNS, OUTLINE, DESCRIPTION, IMAGE_410X250, URL, TIP_TYPE, COLLECT_CNT, PKG_FILE_SIZE_SCOPE, ONLINE_YEAR, TAG_IDS, STATUS, VENDOR_ID, CHANNEL_ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            datalist.append((seq,
                             channelTO.getId(),
                             channelTO.getName(),
                             channelTO.getEnName(),
                             channelTO.getPinyin(),
                             channelTO.getCategoryId(),
                             channelTO.getCategoryName(),
                             channelTO.getCategoryTabFlagSet(),
                             channelTO.getResourceType(),
                             channelTO.getComments(),
                             channelTO.getHotCnt(),
                             channelTO.getStars(),
                             channelTO.getPublishDate(),
                             channelTO.getIcon(),
                             channelTO.getBanner(),
                             channelTO.getCopyrightType(),
                             channelTO.getGoodRatingCnt(),
                             channelTO.getPkgFileSize(),
                             channelTO.getSreenSizeSet(),
                             channelTO.getMinSdk(),
                             channelTO.getLastestVerName(),
                             channelTO.getCreatedDate(),
                             channelTO.getPkgCreatedDate(),
                             channelTO.getDataType(),
                             channelTO.getLanguageType(),
                             channelTO.getPkgChannelFlagSet(),
                             channelTO.getScore(),
                             channelTO.getDowns(),
                             channelTO.getOutline(),
                             channelTO.getDescription(),
                             channelTO.getImage_410X250(),
                             channelTO.getUrl(),
                             channelTO.getTipType(),
                             channelTO.getCollectCnt(),
                             channelTO.getPkgFileSizeScope(),
                             channelTO.getOnlineYear(),
                             channelTO.getTagIds(),
                             channelTO.getStatus(),
                             channelTO.getVendorId(),
                             channelTO.getChannelId()))
            seq += 1
            if len(datalist)>=1000:
                cursor.executemany(sql, tuple(datalist))
                conn.commit()
                datalist = []
                
        if datalist:
            cursor.executemany(sql, tuple(datalist))
            conn.commit()
            datalist = []

    print "insert success, tableName:%s, count:%d" %(tableName, seq)
#更新保存最新排序列表的表名
def updateTableName(sortType, tableName):
    type2 = TYPE_DIC[sortType]
    sql = "update GAME_LIST_TABLE_STATUS set TABLE_NAME = '%s', UPDATE_TIME = '%s' where TYPE = '%s'" % (tableName, datetime.datetime.now(),type2)
    cursor.execute(sql)
    conn.commit()

#插入排序后的列表信息到数据库中
def insertSortList(sortType, sortList, advLanguaged):
    #获取待操作表名
    tableName = ''
    tableName = getTableNameForInsert(sortType)
    print 'tableName: %s' % tableName

    #清空待操作表
    clearTable(tableName)

    #插入数据
    print 'start insert'
    insertResourceInfos(tableName, sortList, advLanguaged)
    print 'end insert'

    #更新保存最新排序列表的表名
    updateTableName(sortType, tableName)

#根据sortType处理某个列表
def handleBySortType(sortType, advLanguaged = False):
    #获取排序后的列表信息
    sortList = getSortList(sortType, advLanguaged)

    #插入排序后的列表信息到数据库中
    insertSortList(sortType, sortList, advLanguaged)
  
#专区TO
class ChannelTO:
    def __init__(self):
        self.id = None
        self.channelId = None
        self.name = None
        self.enName = None
        self.pinyin = None
        self.resourceType = None
        self.hotCnt = None
        self.stars = None
        self.score = None
        self.outline = None
        self.description = None
        self.icon = None
        self.banner = None
        self.image_410X250 = None
        self.collectCnt = None
        self.dataType = None
        self.tipType = None
        self.categoryId = None
        self.categoryName = None
        self.categoryTabFlagSet = None
        self.tagIds = None
        self.lastestVerName = None
        self.publishDate = None
        self.createdDate = None
        self.pkgFileSize = None
        self.pkgCreatedDate = None
        self.pkgFileSizeScope = None
        self.onlineYear = None
        self.vendorId = None
        self.languageType = None
        self.comments = None
        self.goodRatingCnt = None
        self.minSdk = None
        self.sreenSizeSet = None
        self.copyrightType = None
        self.downs = None
        self.url = None
        self.status = None
        self.pkgChannelFlagSet = None
        self.advLanguageType = None
        
    def setId(self, id):
        self.id = id
        
    def getId(self):
        return self.id    
    
    def setChannelId(self, channelId):
        self.channelId = channelId
        
    def getChannelId(self):
        return self.channelId
        
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
        
    def setEnName(self, enName):
        self.enName = enName
        
    def getEnName(self):
        return self.enName
        
    def setPinyin(self, pinyin):
        self.pinyin = pinyin
        
    def getPinyin(self):
        return self.pinyin
        
    def setResourceType(self, resourceType):
        self.resourceType = resourceType
        
    def getResourceType(self):
        return self.resourceType
        
    def setHotCnt(self, hotCnt):
        self.hotCnt = hotCnt
        
    def getHotCnt(self):
        return self.hotCnt
        
    def setStars(self, stars):
        self.stars = stars
        
    def getStars(self):
        return self.stars
        
    def setScore(self, score):
        self.score = score
        
    def getScore(self):
        return self.score

    def setOutline(self, outline):
        self.outline = outline
        
    def getOutline(self):
        return self.outline
        
    def setDescription(self, description):
        self.description = description
        
    def getDescription(self):
        return self.description
        
    def setIcon(self, icon):
        self.icon = icon
        
    def getIcon(self):
        return self.icon
        
    def setBanner(self, banner):
        self.banner = banner
        
    def getBanner(self):
        return self.banner
        
    def setImage_410X250(self, image_410X250):
        self.image_410X250 = image_410X250
        
    def getImage_410X250(self):
        return self.image_410X250
 
    def setCollectCnt(self, collectCnt):
        self.collectCnt = collectCnt
        
    def getCollectCnt(self):
        return self.collectCnt 
        
    def setDataType(self, dataType):
        self.dataType = dataType
        
    def getDataType(self):
        return self.dataType 
        
    def setTipType(self, tipType):
        self.tipType = tipType
        
    def getTipType(self):
        return self.tipType 

    def setCategoryId(self, categoryId):
        self.categoryId = categoryId
        
    def getCategoryId(self):
        return self.categoryId

    def setCategoryName(self, categoryName):
        self.categoryName = categoryName
        
    def getCategoryName(self):
        return self.categoryName

    def setCategoryTabFlagSet(self, categoryTabFlagSet):
        self.categoryTabFlagSet = categoryTabFlagSet
        
    def getCategoryTabFlagSet(self):
        return self.categoryTabFlagSet
      
    def setTagIds(self, tagIds):
        self.tagIds = tagIds
        
    def getTagIds(self):
        return self.tagIds
 
    def setLastestVerName(self, lastestVerName):
        self.lastestVerName = lastestVerName
        
    def getLastestVerName(self):
        return self.lastestVerName

    def setPublishDate(self, publishDate):
        self.publishDate = publishDate
        
    def getPublishDate(self):
        return self.publishDate

    def setCreatedDate(self, createdDate):
        self.createdDate = createdDate
        
    def getCreatedDate(self):
        return self.createdDate
        
    def setPkgFileSize(self, pkgFileSize):
        self.pkgFileSize = pkgFileSize
        
    def getPkgFileSize(self):
        return self.pkgFileSize
        
    def setPkgCreatedDate(self, pkgCreatedDate):
        self.pkgCreatedDate = pkgCreatedDate
        
    def getPkgCreatedDate(self):
        return self.pkgCreatedDate
        
    def setPkgFileSizeScope(self, pkgFileSizeScope):
        self.pkgFileSizeScope = pkgFileSizeScope
        
    def getPkgFileSizeScope(self):
        return self.pkgFileSizeScope
        
    def setOnlineYear(self, onlineYear):
        self.onlineYear = onlineYear
        
    def getOnlineYear(self):
        return self.onlineYear
        
    def setVendorId(self, vendorId):
        self.vendorId = vendorId
        
    def getVendorId(self):
        return self.vendorId
        
    def setLanguageType(self, languageType):
        self.languageType = languageType
        
    def getLanguageType(self):
        return self.languageType
        
    def setComments(self, comments):
        self.comments = comments
        
    def getComments(self):
        return self.comments
        
    def setGoodRatingCnt(self, goodRatingCnt):
        self.goodRatingCnt = goodRatingCnt
        
    def getGoodRatingCnt(self):
        return self.goodRatingCnt
        
    def setMinSdk(self, minSdk):
        self.minSdk = minSdk
        
    def getMinSdk(self):
        return self.minSdk
        
    def setSreenSizeSet(self, sreenSizeSet):
        self.sreenSizeSet = sreenSizeSet
        
    def getSreenSizeSet(self):
        return self.sreenSizeSet
        
    def setCopyrightType(self, copyrightType):
        self.copyrightType = copyrightType
        
    def getCopyrightType(self):
        return self.copyrightType

    def setDowns(self, downs):
        self.downs = downs
        
    def getDowns(self):
        return self.downs
        
    def setUrl(self, url):
        self.url = url
        
    def getUrl(self):
        return self.url
    
    def setStatus(self, status):
        self.status = status
        
    def getStatus(self):
        return self.status
        
    def setPkgChannelFlagSet(self, pkgChannelFlagSet):
        self.pkgChannelFlagSet = pkgChannelFlagSet
        
    def getPkgChannelFlagSet(self):
        return self.pkgChannelFlagSet
    
    def setAdvLanguageType(self, advLanguageType):
        self.advLanguageType = advLanguageType
    
    def getAdvLanguageType(self):
        return self.advLanguageType
   
###############################################################
if __name__ == '__main__':
    try:
        #记录开始时间
        startTime = datetime.datetime.now()
        
        #初始化
        initTag()
        print 'initTag success'
        
        initOrgGameList()
        print 'initOrgGameList success'
        
        initOrgSoftwareList()
        print 'initOrgSoftwareList success'
         
        initOrgNetgameList()
        print 'initOrgNetgameList success'
          
        #游戏原始列表
        print '游戏原始列表'
        sortType = GAME_ORIGINAL_LIST
        handleBySortType(sortType)
#           
        #游戏最热列表
        print '游戏最热列表'
        sortType = GAME_HOTEST_LIST
        handleBySortType(sortType, True)
          
        #游戏最新列表
        print '游戏最新列表'
        sortType = GAME_NEWEST_LIST
        handleBySortType(sortType, True)
           
        #游戏五星列表
        print '游戏五星列表'
        sortType = GAME_FIVESTAR_LIST
        handleBySortType(sortType, True)
           
        #软件原始列表
        print '软件原始列表'
        sortType = SOFTWARE_ORIGINAL_LIST
        handleBySortType(sortType)
            
        #软件最热列表
        print '软件最热列表'
        sortType = SOFTWARE_HOTEST_LIST
        handleBySortType(sortType)
            
        #软件最新列表
        print '软件最新列表'
        sortType = SOFTWARE_NEWEST_LIST
        handleBySortType(sortType)
            
        #软件五星列表
        print '软件五星列表'
        sortType = SOFTWARE_FIVESTAR_LIST
        handleBySortType(sortType)
            
        #网游原始列表
        print '网游原始列表'
        sortType = NETGAME_ORIGINAL_LIST
        handleBySortType(sortType)
            
        #网游最热列表
        print '网游最热列表'
        sortType = NETGAME_HOTEST_LIST
        handleBySortType(sortType)
            
        #网游最新列表
        print '网游最新列表'
        sortType = NETGAME_NEWEST_LIST
        handleBySortType(sortType)
            
        #网游五星列表
        print '网游五星列表'
        sortType = NETGAME_FIVESTAR_LIST
        handleBySortType(sortType)

        #记录总共花销时间
        spentTime = datetime.datetime.now() - startTime
        print spentTime
        maxTime = datetime.timedelta(minutes=15)
        if spentTime > maxTime:
             #脚本运行超时，发告警信息到邮箱，有可能数据库性能缓慢~~~
             sendmail('webmaster@downjoy.com', MONITOR_MAIL, "脚本超时", "android 生成广告位列表--脚本超时,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")

        #清理web服务器中的列表状态信息缓存
        #cleanListTableStatusCache()

    except Exception, ex:
        print traceback.format_exc()
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, traceback.format_exc(), "android 生成广告位列表出错,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")
        raise Exception

    finally:
        cursor.close()
        conn.close()
