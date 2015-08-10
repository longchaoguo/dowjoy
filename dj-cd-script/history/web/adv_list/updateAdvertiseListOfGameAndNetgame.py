#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: shan.liang $"
__version__ = "$Revision: 1.00 $"
__date__ = "$Date: 2013/11/21 $"

import MySQLdb
import traceback
import datetime
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import smtplib
import httplib


#异常邮件接收者
MONITOR_MAIL=['zhou.wu@downjoy.com','shan.liang@downjoy.com','xiaodong.zheng@downjoy.com']

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

#web网站服务器IP:port
WEB_IP_LIST = ['192.168.0.211:8080', '192.168.0.155:8080', '192.168.0.167:8080', '192.168.0.174:8080']
DIGUA_IP_LIST = ['192.168.0.211:7011', '192.168.0.155:7011', '192.168.0.167:7011', '192.168.0.174:7011']

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

#调用web服务接口，从web服务的二级缓存中获得列表状态信息
def getListTableStatusJsonByWebSeverIp(webServerIp):
    url = "/djweb/clean/listTableStatus"
    conn = httplib.HTTPConnection(webServerIp)
    conn.request("GET", url)
    res = conn.getresponse()
    data = eval(res.read())
    return data

#调用web服务接口，清理web服务的二级缓存中的列表状态信息
def cleanListTableStatusCache():
    #清除web缓存
    for ip in WEB_IP_LIST:
        url = "/djweb/clean/cleanTableStatus"
        conn = httplib.HTTPConnection(ip)
        conn.request("GET", url)
        res = conn.getresponse()
        data = res.read()

    #清除digua缓存
    for ip in DIGUA_IP_LIST:
        url = "/clean/ablist"
        conn = httplib.HTTPConnection(ip)
        conn.request("GET", url)
        res = conn.getresponse()
        data = res.read()

    #调用预上线四期清理缓存接口，上线后删除以下方法
    url = "/djweb2/clean/cleanTableStatus"
    conn = httplib.HTTPConnection("192.168.0.174:7031")
    conn.request("GET", url)
    data = res.read()
    ############
	#清除newdigua列表缓存
    url = "/newdiguaserver/clean/redis/cleankeyprefix?key=_new_digua_game_newest_list_language"
    conn = httplib.HTTPConnection("api2014.digua.d.cn")
    conn.request("GET", url)
    data = res.read()

    return



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

#判断四个web服务器中，二级缓存中的列表状态信息是否与数据库中的信息一致
def checkListTableStatus():
    #获取数据库中的列表状态信息
    global listTableStatusOfDb
    listTableStatusOfDb = {}
    for sortType, sortTypeName in TYPE_DIC.items():
        tableName = getTableName(sortType)
        listTableStatusOfDb[sortTypeName] = tableName

    #获取二级缓存中的列表状态信息，并做check
    global ERROR_MSG
    ERROR_MSG=""
    #for ip in WEB_IP_LIST:
    #    curListTableStatus = getListTableStatusJsonByWebSeverIp(ip)
    #    curErrorMsg = ""
    #    for key, value in curListTableStatus.items():
    #        if value != listTableStatusOfDb[key]:
    #            ERROR_MSG =  ERROR_MSG + " IP=%s的WEB服务器的二级缓存中，列表%s对应的表为%s, 而数据库中对应的表为%s <br/>" % (str(ip), str(key), str(value), str(listTableStatusOfDb[key]))
    #
    #if (ERROR_MSG != ""):
    #    return False
    return True

#获得资源信息详细信息
def getResourceInfo(resourceId, resourceType):
    resourceInfo = {}
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
                        MIN(P.FILE_SIZE) AS FILE_SIZE,
                        MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                        BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                        MAX(P.MIN_SDK) AS MIN_SDK,
                        BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                        G.COPYRIGHT_TYPE,
                        G.SCORE,
                        G.DOWNS,
                        G.OUTLINE,
                        G.DESCRIPTION,
                        G.IMAGE_410X250,
                        P.URL
                FROM GAME G
                INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
                INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
                WHERE G.ID = %d
                AND G.RESOURCE_TYPE = %d
                AND G.STATUS = 1
                AND P.STATUS = 1''' % (resourceId, resourceType)
        cursor.execute(sql)
        rows = cursor.fetchall()
        if not rows or (len(rows) == 0) or (not rows[0][0]):
            return resourceInfo
        else:
            resourceInfo['RESOURCE_ID'] = rows[0][0]
            resourceInfo['NAME'] = rows[0][1]
            resourceInfo['ENNAME'] = rows[0][2]
            resourceInfo['PINYIN'] = ''
            resourceInfo['CATEGORY_ID'] = rows[0][3]
            resourceInfo['CATEGORY_NAME'] = rows[0][14]
            resourceInfo['RESOURCE_TYPE'] = resourceType
            resourceInfo['COMMENT'] = rows[0][4]
            resourceInfo['HOT_CNT'] = rows[0][5]
            resourceInfo['STARTS'] = rows[0][6]
            resourceInfo['RESOURCE_PUBLISH_DATE'] = rows[0][11]
            resourceInfo['ICON'] = rows[0][7]
            resourceInfo['BANNER'] = rows[0][15]
            resourceInfo['GOOD_RATING_CNT'] = rows[0][13]
            resourceInfo['FILE_SIZE'] = rows[0][16]
            resourceInfo['LATEST_VERSION_NAME'] = rows[0][8]
            resourceInfo['CREATED_DATE'] = rows[0][12]
            resourceInfo['PKG_CREATED_DATE'] = rows[0][17]
            resourceInfo['DATA_TYPE'] = rows[0][9] | 16  #16表示该资源是一个广告位，用于前台角标的展示
            resourceInfo['LANGUAGE_TYPE'] = rows[0][10]
            resourceInfo['PKG_CHANNEL_FLAG_SET'] = rows[0][18]
            resourceInfo['MIN_SDK'] = rows[0][19]
            resourceInfo['SCREEN_SIZE_SET'] = rows[0][20]
            resourceInfo['COPYRIGHT_TYPE'] = rows[0][21]
            resourceInfo['SCORE'] = rows[0][22]
            resourceInfo['DOWNS'] = rows[0][23]
            resourceInfo['OUTLINE'] = rows[0][24]
            resourceInfo['DESCRIPTION'] = rows[0][25]
            resourceInfo['IMAGE_410X250'] = rows[0][26]
            resourceInfo['URL'] = rows[0][27]


    elif resourceType == RESOURCE_TYPE_NETGAME:
        sql = '''SELECT C.ID,
                        C.NAME,
                        C.PINYIN,
                        C.HDICON,
                        C.TAG_NAMES,
                        C.STARS,
                        C.HOT_CNT,
                        C.CREATED_DATE,
                        C.LAST_UPDATE_DATE,
                        G.LAST_VERSION_NUM,
                        MIN(GP.FILE_SIZE),
                        C.BANNER,
                        MAX(GPM.MIN_SDK),
                        BIT_OR(GPM.SCREEN_SIZE_SET),
                        C.SCORE,
                        C.DOWNS,
                        CASE
                            WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                            ELSE C.OUTLET_LINE
                        END AS OUTLINE,
                        C.DESCRIPTION
                FROM NETGAME_CHANNEL C
                LEFT JOIN NETGAME_GAME G ON C.ID = G.CHANNEL_ID
                LEFT JOIN NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
                LEFT JOIN NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
                WHERE C.ID = %d
                AND (C.NETGAME_SYNC_STATUS = 1 || C.NETGAME_SYNC_STATUS = 2)
                AND C.STATUS = 1
                AND (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS = 1 || G.NETGAME_SYNC_STATUS = 2)
                AND (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS = 1 || GP.NETGAME_SYNC_STATUS = 2)
                AND G.CHANNEL_FLAG & 8 = 8''' % resourceId
        cursor.execute(sql)
        rows = cursor.fetchall()
        if not rows or (len(rows) == 0) or (not rows[0][0]):
            return resourceInfo
        else:
            resourceInfo['RESOURCE_ID'] = rows[0][0]
            resourceInfo['NAME'] = rows[0][1]
            resourceInfo['ENNAME'] = ''
            resourceInfo['PINYIN'] = rows[0][2]
            resourceInfo['CATEGORY_ID'] = None
            resourceInfo['CATEGORY_NAME'] = rows[0][4]
            resourceInfo['RESOURCE_TYPE'] = resourceType
            resourceInfo['COMMENT'] = None
            resourceInfo['HOT_CNT'] = rows[0][6]
            resourceInfo['STARTS'] = rows[0][5]
            resourceInfo['RESOURCE_PUBLISH_DATE'] = rows[0][8]
            resourceInfo['ICON'] = rows[0][3]
            resourceInfo['BANNER'] = rows[0][11]
            resourceInfo['GOOD_RATING_CNT'] = None
            resourceInfo['FILE_SIZE'] = rows[0][10]
            resourceInfo['LATEST_VERSION_NAME'] = rows[0][9]
            resourceInfo['CREATED_DATE'] = rows[0][7]
            resourceInfo['PKG_CREATED_DATE'] = None
            resourceInfo['DATA_TYPE'] = 16  #16表示该资源是一个广告位，用于前台角标的展示
            resourceInfo['LANGUAGE_TYPE'] = 7 #网游默认为支持中-2、英-1、韩-4
            resourceInfo['PKG_CHANNEL_FLAG_SET'] = 511
            resourceInfo['MIN_SDK'] = rows[0][12]
            resourceInfo['SCREEN_SIZE_SET'] = rows[0][13]
            resourceInfo['COPYRIGHT_TYPE'] = None
            resourceInfo['SCORE'] = rows[0][14]
            resourceInfo['DOWNS'] = rows[0][15]
            resourceInfo['OUTLINE'] = rows[0][16]
            resourceInfo['DESCRIPTION'] = rows[0][17]
            resourceInfo['IMAGE_410X250'] = None
            resourceInfo['URL'] = None

    return resourceInfo

#获得运营自定义的在列表页中的资源（游戏/软件/网游）排序信息
def getCustomResSortDict(sortType):
    sql = '''SELECT resource_id,
                    resource_type,
                    position
             FROM GAME_LIST_CUSTOM_ADV
             WHERE LIST_TYPE = %d
             ORDER BY position ASC''' % (sortType)
    cursor.execute(sql)
    rows = cursor.fetchall()

    customResSortDict = {}
    if not rows: return customResSortDict
    for row in rows:
        position = int(row[2])
        # 业务规则：网游列表中只能插入网游广告位，游戏/软件过滤掉
        if (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_NETGAME) and (row[1] != RESOURCE_TYPE_NETGAME):
            continue

        #获取广告位资源信息
        resourceInfo = getResourceInfo(row[0], row[1])
        if not resourceInfo:
            continue
        customResSortDict[position] = resourceInfo

    return customResSortDict

#获得游戏/软件原始排序的列表
def getOriginalGameOrSoftwareResSortList(sortType, exclusion_ids):
    sql = ''
    exclusion_ids += ','
    if sortType == GAME_HOTEST_LIST or sortType == SOFTWARE_HOTEST_LIST:
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
                        MIN(P.FILE_SIZE) AS FILE_SIZE,
                        MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                        BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                        MAX(P.MIN_SDK) AS MIN_SDK,
                        BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                        G.COPYRIGHT_TYPE,
                        G.SCORE,
                        G.DOWNS,
                        G.OUTLINE,
                        G.DESCRIPTION,
                        G.IMAGE_410X250,
                        P.URL
                FROM GAME G
                INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
                INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
                WHERE G.RESOURCE_TYPE = %d
                AND G.STATUS > 0
                AND P.STATUS = 1
                GROUP BY G.ID
                ORDER BY G.HOT_CNT DESC''' % (LIST_RESOURCE_TYPE_DIC[sortType])
    elif sortType == GAME_NEWEST_LIST or sortType == GAME_ORIGINAL_LIST or sortType == SOFTWARE_NEWEST_LIST or sortType == SOFTWARE_ORIGINAL_LIST:
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
                        MIN(P.FILE_SIZE) AS FILE_SIZE,
                        MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                        BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                        MAX(P.MIN_SDK) AS MIN_SDK,
                        BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                        G.COPYRIGHT_TYPE,
                        G.SCORE,
                        G.DOWNS,
                        G.OUTLINE,
                        G.DESCRIPTION,
                        G.IMAGE_410X250,
                        P.URL
                FROM GAME G
                INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
                INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
                WHERE G.RESOURCE_TYPE = %d
                AND G.STATUS > 0
                AND P.STATUS = 1
                GROUP BY G.ID
                ORDER BY G.PUBLISH_DATE DESC''' % (LIST_RESOURCE_TYPE_DIC[sortType])
    elif sortType == GAME_FIVESTAR_LIST or sortType == SOFTWARE_FIVESTAR_LIST:
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
                        MIN(P.FILE_SIZE) AS FILE_SIZE,
                        MAX(P.CREATED_DATE) AS P_CREATED_DATE,
                        BIT_OR(P.CHANNEL_FLAG_SET & P.SYNC_CHANNEL_FLAG_SET),
                        MAX(P.MIN_SDK) AS MIN_SDK,
                        BIT_OR(P.SCREEN_SIZE_SET) AS SCREEN_SIZE_SET,
                        G.COPYRIGHT_TYPE,
                        G.SCORE,
                        G.DOWNS,
                        G.OUTLINE,
                        G.DESCRIPTION,
                        G.IMAGE_410X250,
                        P.URL
                FROM GAME G
                INNER JOIN GAME_CATEGORY C ON G.GAME_CATEGORY_ID = C.ID
                INNER JOIN GAME_PKG P ON P.GAME_ID = G.ID
                WHERE G.STARS = 5
                AND G.RESOURCE_TYPE = %d
                AND G.STATUS > 0
                AND P.STATUS = 1
                GROUP BY G.ID
                ORDER BY G.PUBLISH_DATE DESC''' % (LIST_RESOURCE_TYPE_DIC[sortType])
    else:
        return []

    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        curSql = sql + ' limit %s, %s'
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(curSql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum

    originalResSortList = []
    if not allRows:
        return originalResSortList
    for row in allRows:
        #将WEB/WAP/DIGUA渠道都没有同步好的游戏过滤出去（1：WEB  2: WAP  4：DIGUA）
        if (row[18] == 0) or ((row[18] & 1 == 0) and (row[18] & 2 == 0) and (row[18] & 4 == 0)):
            continue
            #将广告位的游戏过滤
        if exclusion_ids.find(',' + str(row[0]) + ',') != -1:
            continue
        resourceInfo = {}
        resourceInfo['RESOURCE_ID'] = row[0]
        resourceInfo['NAME'] = row[1]
        resourceInfo['ENNAME'] = row[2]
        resourceInfo['PINYIN'] = ''
        resourceInfo['CATEGORY_ID'] = row[3]
        resourceInfo['CATEGORY_NAME'] = row[14]
        resourceInfo['RESOURCE_TYPE'] = LIST_RESOURCE_TYPE_DIC[sortType]
        resourceInfo['COMMENT'] = row[4]
        resourceInfo['HOT_CNT'] = row[5]
        resourceInfo['STARTS'] = row[6]
        resourceInfo['RESOURCE_PUBLISH_DATE'] = row[11]
        resourceInfo['ICON'] = row[7]
        resourceInfo['BANNER'] = row[15]
        resourceInfo['GOOD_RATING_CNT'] = row[13]
        resourceInfo['FILE_SIZE'] = row[16]
        resourceInfo['LATEST_VERSION_NAME'] = row[8]
        resourceInfo['CREATED_DATE'] = row[12]
        resourceInfo['PKG_CREATED_DATE'] = row[17]
        resourceInfo['DATA_TYPE'] = row[9]
        resourceInfo['LANGUAGE_TYPE'] = row[10]
        resourceInfo['PKG_CHANNEL_FLAG_SET'] = row[18]
        resourceInfo['MIN_SDK'] = row[19]
        resourceInfo['SCREEN_SIZE_SET'] = row[20]
        resourceInfo['COPYRIGHT_TYPE'] = row[21]
        resourceInfo['SCORE'] = row[22]
        resourceInfo['DOWNS'] = row[23]
        resourceInfo['OUTLINE'] = row[24]
        resourceInfo['DESCRIPTION'] = row[25]
        resourceInfo['IMAGE_410X250'] = row[26]
        resourceInfo['URL'] = row[27]
        originalResSortList.append(resourceInfo)

    return originalResSortList

#获得网游原始排序的列表
def getOriginalNetgameResSortList(sortType, exclusion_ids):
    sql = ''
    if sortType == NETGAME_HOTEST_LIST:
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
                    MIN(GP.FILE_SIZE),
                    C.BANNER,
                    MAX(GPM.MIN_SDK),
                    BIT_OR(GPM.SCREEN_SIZE_SET),
                    C.TAG_IDS,
                    C.SCORE,
                    C.DOWNS,
                    CASE
                        WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                        ELSE C.OUTLET_LINE
                    END AS OUTLINE,
                    C.DESCRIPTION
            from NETGAME_CHANNEL C
            left join NETGAME_GAME G ON C.ID = G.CHANNEL_ID
            left join NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
            left join NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
            where (C.NETGAME_SYNC_STATUS = 1 || C.NETGAME_SYNC_STATUS = 2)
            and C.STATUS = 1
            and (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS = 1 || G.NETGAME_SYNC_STATUS = 2)
            and (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS = 1 || GP.NETGAME_SYNC_STATUS = 2)
            and C.ID NOT IN (%s)
            group by C.ID
            order by C.HOT_CNT desc''' % exclusion_ids
    elif sortType == NETGAME_NEWEST_LIST or sortType == NETGAME_ORIGINAL_LIST:
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
                    MIN(GP.FILE_SIZE),
                    C.BANNER,
                    MAX(GPM.MIN_SDK),
                    BIT_OR(GPM.SCREEN_SIZE_SET),
                    C.TAG_IDS,
                    C.SCORE,
                    C.DOWNS,
                    CASE
                        WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                        ELSE C.OUTLET_LINE
                    END AS OUTLINE,
                    C.DESCRIPTION
            from NETGAME_CHANNEL C
            left join NETGAME_GAME G ON C.ID = G.CHANNEL_ID
            left join NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
            left join NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
            where (C.NETGAME_SYNC_STATUS = 1 || C.NETGAME_SYNC_STATUS = 2)
            and C.STATUS = 1
            and (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS = 1 || G.NETGAME_SYNC_STATUS = 2)
            and (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS = 1 || GP.NETGAME_SYNC_STATUS = 2)
            and C.ID NOT IN (%s)
            group by C.ID
            order by C.LAST_UPDATE_DATE desc''' % exclusion_ids
    elif sortType == NETGAME_FIVESTAR_LIST:
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
                    MIN(GP.FILE_SIZE),
                    C.BANNER,
                    MAX(GPM.MIN_SDK),
                    BIT_OR(GPM.SCREEN_SIZE_SET),
                    C.TAG_IDS,
                    C.SCORE,
                    C.DOWNS,
                    CASE
                        WHEN(C.OUTLET_LINE IS NULL) THEN C.SLOGAN
                        ELSE C.OUTLET_LINE
                    END AS OUTLINE,
                    C.DESCRIPTION
            from NETGAME_CHANNEL C
            left join NETGAME_GAME G ON C.ID = G.CHANNEL_ID
            left join NETGAME_GAME_PKG GP ON GP.GAME_ID = G.ID
            left join NETGAME_GAME_PKG_MANIFEST GPM ON GP.ID = GPM.PID
            where C.STARS = 5
            and (C.NETGAME_SYNC_STATUS = 1 || C.NETGAME_SYNC_STATUS = 2)
            and C.STATUS = 1
            and (G.NETGAME_SYNC_STATUS IS NULL || G.NETGAME_SYNC_STATUS = 1 || G.NETGAME_SYNC_STATUS = 2)
            and (GP.NETGAME_SYNC_STATUS IS NULL || GP.NETGAME_SYNC_STATUS = 1 || GP.NETGAME_SYNC_STATUS = 2)
            and C.ID NOT IN (%s)
            group by C.ID
            order by C.LAST_UPDATE_DATE desc''' % exclusion_ids
    else:
        return []

    startIdx = 0
    pageNum = 1000
    allRows = []
    while True:
        curSql = sql + ' limit %s, %s'
        datalist = []
        datalist.append((startIdx, pageNum))
        cursor.executemany(curSql, tuple(datalist))
        rows = cursor.fetchall()
        if not rows:
            break
        else:
            allRows.extend(rows)
            startIdx += pageNum

    originalResSortList = []
    if not allRows:
        return originalResSortList
    for row in allRows:
        resourceInfo = {}
        resourceInfo['RESOURCE_ID'] = row[0]
        resourceInfo['NAME'] = row[1]
        resourceInfo['ENNAME'] = ''
        resourceInfo['PINYIN'] = row[2]
        resourceInfo['CATEGORY_ID'] = row[14]
        resourceInfo['CATEGORY_NAME'] = row[4]
        resourceInfo['RESOURCE_TYPE'] = 5
        resourceInfo['COMMENT'] = None
        resourceInfo['HOT_CNT'] = int(row[6])
        resourceInfo['STARTS'] = row[5]
        resourceInfo['RESOURCE_PUBLISH_DATE'] = row[8]
        resourceInfo['ICON'] = row[3]
        resourceInfo['BANNER'] = row[11]
        resourceInfo['GOOD_RATING_CNT'] = None
        resourceInfo['FILE_SIZE'] = row[10]
        resourceInfo['LATEST_VERSION_NAME'] = row[9]
        resourceInfo['CREATED_DATE'] = row[7]
        resourceInfo['PKG_CREATED_DATE'] = None
        resourceInfo['DATA_TYPE'] = 0
        resourceInfo['LANGUAGE_TYPE'] = 7 #网游默认支持中-2、英-1、韩-4
        resourceInfo['PKG_CHANNEL_FLAG_SET'] = 511
        resourceInfo['MIN_SDK'] = row[12]
        resourceInfo['SCREEN_SIZE_SET'] = row[13]
        resourceInfo['COPYRIGHT_TYPE'] = None
        resourceInfo["SCORE"] = str(row[15])
        resourceInfo["DOWNS"] = row[16]
        resourceInfo["OUTLINE"] = row[17]
        resourceInfo["DESCRIPTION"] = row[18]
        resourceInfo['IMAGE_410X250'] = None
        resourceInfo['URL'] = None
        originalResSortList.append(resourceInfo)

    return originalResSortList

#获得有广告位插入、排序后的列表
def getAdvertiseSortList(sortType):
    #运营自定义排序
    customResSortDict = getCustomResSortDict(sortType)
    print 'custom rows len: %d' % (len(customResSortDict))

    #获取需要从原始排序中去除的资源ID
    exclusion_ids = '0'
    for resInfo in customResSortDict.values():
        if resInfo['RESOURCE_TYPE'] == LIST_RESOURCE_TYPE_DIC[sortType]:
            exclusion_ids = exclusion_ids + ',' + str(resInfo['RESOURCE_ID'])
    print exclusion_ids

    #原始排序
    originalResSortList = []
    if (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_GAME) or (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_SOFTWARE):
        originalResSortList = getOriginalGameOrSoftwareResSortList(sortType, exclusion_ids)
    else:
        originalResSortList = getOriginalNetgameResSortList(sortType, exclusion_ids)
    print 'orignal rows len: %d' % (len(originalResSortList))

    #获得最终排序结果
    keys = customResSortDict.keys()
    keys.sort()
    for position in keys:
        if (position < 1) or (position > len(originalResSortList)): continue
        originalResSortList.insert(position - 1, customResSortDict[position])
    print 'final rows len: %d' % len(originalResSortList)

    return originalResSortList

#获取原始排序列表
def getOriginalSortList(sortType):
    originalResSortList = []
    exclusion_ids = '0'
    if (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_GAME) or (LIST_RESOURCE_TYPE_DIC[sortType] == RESOURCE_TYPE_SOFTWARE):
        originalResSortList = getOriginalGameOrSoftwareResSortList(sortType, exclusion_ids)
    else:
        originalResSortList = getOriginalNetgameResSortList(sortType, exclusion_ids)
    print 'orignal rows len: %d' % (len(originalResSortList))

    return originalResSortList

#获得最终排序好的列表
def getSortList(sortType):
    if sortType in NOT_ADVERTISE_LIST:
        return getOriginalSortList(sortType)
    else:
        return getAdvertiseSortList(sortType)

#获取待操作的表名
def getTableNameForInsert(sortType):
    sortTypeName = TYPE_DIC[sortType]
    tableName = listTableStatusOfDb[sortTypeName]
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

#插入排序后的列表信息
def insertResourceInfos(tableName, sortList):
    sql = ''
    seq = 1
    if not sortList: return
    datalist = []

    for resourceInfo in sortList:
        sql = "INSERT INTO %s " % tableName
        sql += "(ID, RESOURCE_ID, NAME, ENNAME, PINYIN, CATEGORY_ID, CATEGORY_NAME, RESOURCE_TYPE, COMMENT, HOT_CNT, STARS, RESOURCE_PUBLISH_DATE, ICON, BANNER, GOOD_RATING_CNT, FILE_SIZE, LATEST_VERSION_NAME, CREATED_DATE, PKG_CREATED_DATE, DATA_TYPE, LANGUAGE_TYPE, PKG_CHANNEL_FLAG_SET, MIN_SDK, SCREEN_SIZE_SET,COPYRIGHT_TYPE,SCORE,DOWNS,OUTLINE,DESCRIPTION,IMAGE_410X250,URL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)"
        datalist.append((seq,
                         resourceInfo['RESOURCE_ID'],
                         resourceInfo['NAME'],
                         resourceInfo['ENNAME'],
                         resourceInfo['PINYIN'],
                         resourceInfo['CATEGORY_ID'],
                         resourceInfo['CATEGORY_NAME'],
                         resourceInfo['RESOURCE_TYPE'],
                         resourceInfo['COMMENT'],
                         resourceInfo['HOT_CNT'],
                         resourceInfo['STARTS'],
                         resourceInfo['RESOURCE_PUBLISH_DATE'],
                         resourceInfo['ICON'],
                         resourceInfo['BANNER'],
                         resourceInfo['GOOD_RATING_CNT'],
                         resourceInfo['FILE_SIZE'],
                         resourceInfo['LATEST_VERSION_NAME'],
                         resourceInfo['CREATED_DATE'],
                         resourceInfo['PKG_CREATED_DATE'],
                         resourceInfo['DATA_TYPE'],
                         resourceInfo['LANGUAGE_TYPE'],
                         resourceInfo['PKG_CHANNEL_FLAG_SET'],
                         resourceInfo['MIN_SDK'],
                         resourceInfo['SCREEN_SIZE_SET'],
                         resourceInfo['COPYRIGHT_TYPE'],
                         resourceInfo['SCORE'],
                         resourceInfo['DOWNS'],
                         resourceInfo['OUTLINE'],
                         resourceInfo['DESCRIPTION'],
                         resourceInfo['IMAGE_410X250'],
						 resourceInfo['URL']))
        seq += 1
        if len(datalist)>=1000:
            cursor.executemany(sql, tuple(datalist))
            conn.commit()
            datalist = []
    if datalist:
        cursor.executemany(sql, tuple(datalist))
        conn.commit()
        datalist = []

#更新保存最新排序列表的表名
def updateTableName(sortType, tableName):
    type2 = TYPE_DIC[sortType]
    sql = "update GAME_LIST_TABLE_STATUS set TABLE_NAME = '%s', UPDATE_TIME = '%s' where TYPE = '%s'" % (tableName, datetime.datetime.now(),type2)
    cursor.execute(sql)
    conn.commit()

#插入排序后的列表信息到数据库中
def insertSortList(sortType, sortList):
    #获取待操作表名
    tableName = ''
    tableName = getTableNameForInsert(sortType)
    print 'tableName: %s' % tableName

    #清空待操作表
    clearTable(tableName)

    #插入数据
    print 'start insert'
    insertResourceInfos(tableName, sortList)
    print 'end insert'

    #更新保存最新排序列表的表名
    updateTableName(sortType, tableName)

#根据sortType处理某个列表
def handleBySortType(sortType):
    #获取排序后的列表信息
    sortList = getSortList(sortType)

    #插入排序后的列表信息到数据库中
    insertSortList(sortType, sortList)

###############################################################
if __name__ == '__main__':
    try:
        #判断四个web服务器中，二级缓存中的列表状态信息是否与数据库中的信息一致
        checkRes = checkListTableStatus()
        if not checkRes:
            sendmail('webmaster@downjoy.com', MONITOR_MAIL, ERROR_MSG, "android 生成广告位列表出错--check缓存失败,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")
        else:
            #记录开始时间
            startTime = datetime.datetime.now()

            #游戏原始列表
            print '游戏原始列表'
            sortType = GAME_ORIGINAL_LIST
            handleBySortType(sortType)

            #游戏最热列表
            print '游戏最热列表'
            sortType = GAME_HOTEST_LIST
            handleBySortType(sortType)

            #游戏最新列表
            print '游戏最新列表'
            sortType = GAME_NEWEST_LIST
            handleBySortType(sortType)

            #游戏五星列表
            print '游戏五星列表'
            sortType = GAME_FIVESTAR_LIST
            handleBySortType(sortType)

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
            maxTime = datetime.timedelta(minutes=15)
            if spentTime > maxTime:
                 #脚本运行超时，发告警信息到邮箱，有可能数据库性能缓慢~~~
                 sendmail('webmaster@downjoy.com', MONITOR_MAIL, "脚本超时", "android 生成广告位列表--脚本超时,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")

            #清理web服务器中的列表状态信息缓存
            cleanListTableStatusCache()

    except Exception, ex:
        #print(sys.exc_info()[0],sys.exc_info()[1])
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, traceback.format_exc(), "android 生成广告位列表出错,211.147.5.167_usr_local_bin_changeAndroidGameCustomList.py")
        raise Exception

    finally:
        cursor.close()
        conn.close()
