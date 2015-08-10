#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: helin $"
__version__ = "$Revision: 1.9 $"
__date__ = "$Date: 2013/11/28 20:04:00 $"


import MySQLdb
import urllib
import smtplib
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
import time
import datetime
import re
import stomp
import hashlib

COPYRIGHT_TYPE = "0"
SYNC_STATUS_FILE = "/usr/local/bin/cdroid_business/cdroid_file_sync_check_task_running_copyright_%s.txt"%(COPYRIGHT_TYPE)
SERVERNODE_ARRAY = {}
DEFAULT_URL="http://c.downandroid.com/android/new/game1/"
DEFAULT_URL_PREFIX="http://c.downandroid.com/android/"
MONITOR_MAIL=['shan.liang@downjoy.com','zhou.wu@downjoy.com']

PASSWD = "android.d.cn.cd.20130711"

#��Ҫ���͵�url
NeedUpdateUrls = {}
#��Ҫ���͵�cdnԴվ�ڵ��cdn�����Ķ�Ӧ��ϵ
SERVER_NODE_URL_MAP = {}
#��Ҫ���͵�cdnԴվ�ڵ�������Ķ�Ӧ��ϵ
SERVER_NODE_CHANNEL_MAP = {}

#��ȡcdnԴվ�ڵ��Ӧ�������б�
def getServerNodeChannelMap():
    sql="SELECT server_node_id,channel_flag FROM SERVER_NODE_LINK_CHANNEL WHERE copyright=%s"%(COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs = cursor.fetchall()
    for row in rs:
        server_node_id = row[0]
        channel_flag = row[1]
        if server_node_id in SERVER_NODE_CHANNEL_MAP :
            mapitem = SERVER_NODE_CHANNEL_MAP[server_node_id]
            mapitem.append(channel_flag)
        else :
            mapitem = [channel_flag]
            SERVER_NODE_CHANNEL_MAP[server_node_id] = mapitem

#���°��Ѿ�ͬ���õ�������Ϣ
def updateSyncFinishChannel(serverNodeId,pkgId):
    if serverNodeId not in SERVER_NODE_CHANNEL_MAP:
        return
    mapitem = SERVER_NODE_CHANNEL_MAP[serverNodeId]
    for channel_flag in mapitem:
        sql="update GAME_PKG set SYNC_CHANNEL_FLAG_SET=SYNC_CHANNEL_FLAG_SET+%s where id=%s and SYNC_CHANNEL_FLAG_SET & %s !=%s"%(channel_flag,pkgId,channel_flag,channel_flag)
        cursor.execute(sql)
        conn.commit()

#��ȡcdnԴվ�ڵ��Ӧ��������cdn�����ṩ��
def getServerNodeUrlMap():
    sql="select u.prefix, u.server_node_id,u.cdn_vendor from PUBLISH_URL_PREFIX u where u.need_push=1 and  u.is_cdn=1 and u.status=1 and u.copyright=%s"%(COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs = cursor.fetchall()
    for row in rs:
        prefix = row[0]
        serverNodeId = row[1]
        vendor = row[2]
        if serverNodeId in SERVER_NODE_URL_MAP :
            mapitem = SERVER_NODE_URL_MAP[serverNodeId]
            mapitem[prefix] = vendor
        else :
            mapitem = {prefix:vendor}
            SERVER_NODE_URL_MAP[serverNodeId] = mapitem

#��¼��Ҫ���͸�cdn��url,�����������͸�ָ��ýڵ��cdn��������������cdn��������ֹcdn��������
def recordSyncFinishUrl(url,serverNodeId):
    if serverNodeId not in SERVER_NODE_URL_MAP:
        return
    mapitem = SERVER_NODE_URL_MAP[serverNodeId]
    for prefix, vendor in mapitem.items():
        url = url.replace(DEFAULT_URL_PREFIX, prefix)
        NeedUpdateUrls[url] = vendor

def notifyCDN():
    dunionUrls = ""
    wangsuUrls = ""
    for url, vendor in NeedUpdateUrls.items():
        url = url.strip().lstrip().rstrip()
        if "dilian" == vendor:
            dunionUrls = dunionUrls + ","+url
        elif "wangsu" == vendor:
            wangsuUrls = wangsuUrls + ";"+url
    if len(dunionUrls) > 1 :
        dunionUrls = dunionUrls[1:]
        notifyDunionCDN(dunionUrls)
    if len(wangsuUrls) > 1 :
        wangsuUrls = wangsuUrls[1:]
        notifyWangsuCDN(wangsuUrls)

#�������ݸ�����
def notifyDunionCDN(url):
    readCode=""
    try:
        data={}
        data['username']='cdnpush'
        data['password']='cdn123!@#push'
        data['type']='1'
        data['url']=url.replace("\r\n", "")
        data['decode']='n'
        url="http://pushwt.dnion.com/cdnUrlPush.do"
        aa=urllib.urlencode(data)
        fp=urllib.urlopen(url,urllib.urlencode(data))
        readCode=fp.read()
        fp.close()
        print "push content to dunion,result=%s"%(readCode)
    except Exception,ex:
        print ex
    finally:
        return

#�������ݸ�����
def notifyWangsuCDN(url):
    username='push'
    password='push123!@#'
    readCode=""
    try:
        param={}
        param['username']=username
        param['passwd']=md5hex("%s%s%s"%(username,password,url))
        param['url']=url
        url="http://wscp.lxdns.com:8080/wsCP/servlet/contReceiver"
        f=urllib.urlopen(url,urllib.urlencode(param))
        readCode=f.read()
        f.close()
        print "push content to wangsu,result=%s"%(readCode)
    except Exception,ex:
        print ex
    finally:
        return

def md5hex(word):
    """ MD5�����㷨������32λСд16���Ʒ��� """
    if isinstance(word, unicode):
        word = word.encode("utf-8")
    elif not isinstance(word, str):
        word = str(word)
    m = hashlib.md5()
    m.update(word)
    return m.hexdigest()

#����ļ���СΪ0�����3�Σ���С������ɷ����ļ���С��������
def getFileSize(url):
    retryTime = 3
    fileSize = 0
    while retryTime > 0:
        fileSize = getFileSizeFromUrl(url)
        retryTime = retryTime - 1
        if fileSize > 0:
            return fileSize
    return fileSize
        
#��ȡԶ�̷��������ļ���С
def getFileSizeFromUrl(url):
    fileSize="0"
    try:
        fp=urllib.urlopen(url)
        #print url
        fileSize=fp.read()
        fp.close()
    finally:
        if str.isdigit(fileSize):
            return long(fileSize)
        else:
            return long(0)

def sendmail(From, To, msgBody, title):
    body = "���������ļ���С�����ݿ��fileSize��С��һ��:<br/><br/>��Ϸid|��id|�ļ���С|�ع�-����1(d.androidgame-store.com)|�ٶ�-����2(u.androidgame-store.com)|��ͨ-�żҿ�1(xp.androidgame-store.com)|��ͨ-�żҿ�2(xp2.androidgame-store.com)|����-����1(up.androidgame-store.com)|����-����2(ub2.androidgame-store.com)|���ݿ��ļ���С&nbsp;&nbsp;&nbsp;&nbsp;<br/><br/>%s"%(msgBody)
    server = smtplib.SMTP("mail.downjoy.com")
    server.login("webmaster@downjoy.com","htbp3dQ1sGcco!q")
    main_msg = email.MIMEMultipart.MIMEMultipart()
    text_msg = email.MIMEText.MIMEText(body, 'html', 'gb2312')
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

def notifyWandoujia():
    try:
        fp=urllib.urlopen("http://appapi.wandoujia.com/app/getNotification.php?key=00038492e617e3eef2bf0da9094b2ea9")
        fp.read()
        fp.close()
        #print "notice wandoujia"
    finally:
        print "try notice wandoujia"  

def getServerNodeInfos():
    sql="select ID,IP,ABSOLUTE_DIR from SERVER_NODE where COPYRIGHT=%s and NEED_SYNC=1 and STATUS = 1"%(COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs = cursor.fetchall()
    i = 0
    for row in rs:
	#print row
        id = row[0]
        ip = row[1]
        dir = row[2]
        SERVERNODE_ARRAY[i]=[id, ip, dir]
        i = i+1

#���ĳ�����Ƿ�ͬ����ɣ�
#  ���ͬ����ɣ�����"yes"
#  ���û��ͬ����ɣ�����û�г�ʱ������"no"
#  ���û��ͬ����ɣ����ҳ�ʱ�ˣ�����û����ɵ�ip�б�ƴ�ӳ�һ���ַ�����
def checkSyncFinish(url,pkgFileSize,pkgId,gId,createdDate):
    timeout = 2
    now=time.localtime()
    delayhours=(time.mktime(now)-time.mktime(createdDate))/3600
    sql="select SERVER_NODE_SET from GAME_PKG_EXT where GAME_PKG_ID=%s"%(pkgId)
    cursor.execute(sql)
    rs = cursor.fetchall()
    if len(rs) > 0:
        serverNodeSet = rs[0][0]
    else:
        serverNodeSet = 0
    realserverNodeSet = 0
    msg = ""
    missed_serverNodeIps="";
    for num in range(len(SERVERNODE_ARRAY)):
        serverNodeId = SERVERNODE_ARRAY[num][0]
        serverNodeIp = SERVERNODE_ARRAY[num][1]
        serverNodeDir = SERVERNODE_ARRAY[num][2]
        realserverNodeSet = realserverNodeSet + serverNodeId
        
        if serverNodeDir.find("e:")>-1 or serverNodeDir.find("d:")>-1 :
            filePath = url.replace(DEFAULT_URL, serverNodeDir).replace("/", "\\")
            requestUrl = "http://%s:11010/file.asp?path=%s"%(serverNodeIp, filePath)
            fileSize=getFileSize(requestUrl)
        else:
            filePath = url.replace(DEFAULT_URL, serverNodeDir)
            #http://58.215.241.59:10010/resopt/file?path=/usr/local/django/cdroid_py_cdn.zip&auth=d9facb576476280c1da68d5427a35d6a
            md5 = md5hex("%s%s"%(filePath,PASSWD))
            requestUrl = "http://%s:10010/resopt/file?path=%s&auth=%s"%(serverNodeIp, filePath,md5)
            fileSize=getFileSize(requestUrl)
        
        #print requestUrl+"--------"+str(fileSize)
        #msg="id:%s-pkgId:%s-pkgFileSize:%s-ip:%s====fileSize:%s====serverNodeSet:%s-serverNodeId:%s\n"%(str(gId), str(pkgId), str(pkgFileSize), str(serverNodeIp), str(fileSize), str(serverNodeSet), str(serverNodeId))
        if pkgFileSize == fileSize :
            if serverNodeSet == 0:
                serverNodeSet = serverNodeSet + serverNodeId
                sql="insert into GAME_PKG_EXT(SERVER_NODE_SET, GAME_PKG_ID) values(%s, %s)"%(serverNodeId, pkgId)
                #print sql
                cursor.execute(sql)
                conn.commit()
            elif serverNodeSet & serverNodeId != serverNodeId:
                serverNodeSet = serverNodeSet + serverNodeId
                sql="update GAME_PKG_EXT set SERVER_NODE_SET = SERVER_NODE_SET + %s where GAME_PKG_ID = %s "%(serverNodeId, pkgId)
                cursor.execute(sql)
                conn.commit()
            recordSyncFinishUrl(url,serverNodeId)
            updateSyncFinishChannel(serverNodeId,pkgId)
        else :
            missed_serverNodeIps = missed_serverNodeIps+" "+serverNodeIp;
    if realserverNodeSet == serverNodeSet:
        #ͬ�����
        return "yes"
    elif realserverNodeSet != serverNodeSet and delayhours < timeout:
        #ͬ��δ��ɣ�����û�г�ʱ
        return "no"
    elif realserverNodeSet != serverNodeSet and delayhours >= timeout:
        #ͬ��δ��ɣ����ҳ�ʱ��
        errorInfo="serverNodeIp:%s<br/>game_id:%s<br/>pkg_id:%s<br/>url:%s<br/>pkgFileSize:%s<br/>createdDate:%s<br/><br/>"%(missed_serverNodeIps,gId,pkgId,url,pkgFileSize,time.strftime("%Y-%m-%d %H:%M:%S", createdDate))
        return errorInfo

#���ͬ�����ˣ��޸���ص�״̬
def changeSyncFinishedStatus(pkgId):
    sql1="update GAME_PKG set SYNC_STATUS = 1 where ID = %s"%(pkgId)
    cursor.execute(sql1)
    conn.commit()
    sql2="delete from GAME_PKG_EXT where GAME_PKG_ID = %s"%(pkgId)
    cursor.execute(sql2)
    conn.commit()

def checkPkgExist(pkgId):
    sql="select id from GAME_PKG where id=%s"%(pkgId)
    cursor.execute(sql)
    rs = cursor.fetchall()
    if len(rs) < 1:
        return False
    else:
        return True

#���µİ��滻�ɵİ�
# pkgId : �°���id
# gId : ��Ϸid
# md5 : �°���md5ֵ
# replacePkgId : �ɰ���id
def replaceOldPkgWithNew(newPkgId,gId,md5,oldPkgId):
    
    #��1������ѯ�°��Ƿ���֮ǰ��Ϊmd5ֵ�ظ����Ѿ���ɾ���ˣ������ִ�����������
    #      ���ܵ��µĺ���ǣ�md5ֵ�ظ���2�����������ཫ�Է�ɾ����
    if checkPkgExist(newPkgId) == False:
        #�°���Ϊmd5�ظ����Ѿ���ɾ����,ʲôҲ������ֱ�ӷ���
        return;
    
    #��2������ѯ��Ҫɾ���İ�id�����滻�İ��Լ������Ĺ���
    sql="select concat('',id) as id from GAME_PKG where original_id=%s or id=%s"%(oldPkgId,oldPkgId)
    cursor.execute(sql)
    rs = cursor.fetchall()
    toDeleteIds="0"
    if len(rs) > 0:
        for row in rs:
            toDeleteIds = toDeleteIds + "," + row[0]
    
    #��3��������ص����ݼ�¼��GAME_PKG_HISTORY���У��Ա���ڵ�����һ��ʱ����ȴ�󣬴�cdnԴվ��ɾ����
    sql="insert into GAME_PKG_HISTORY(game_id,pkg_id,file_size,md5,package_name,version_name,created_by,version_code,url,created_date,publish_date) select game_id,id,file_size,md5,package_name,version_name,created_by,version_code,url,created_date,now() from GAME_PKG where id in (%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()

    #��4����ɾ����GAME_PKG_MANIFEST���ж�Ӧ������
    sql="delete from GAME_PKG_MANIFEST where pid in(%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()
    #��5����ɾ����GAME_PKG_CHANNEL���ж�Ӧ������
    sql="delete from GAME_PKG_CHANNEL where game_pkg_id in(%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()
    
    #��6����ɾ����GAME_PKG���ж�Ӧ������
    sql="delete from GAME_PKG where id in (%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()

    #��7�������°��й����ľɰ�id�����
    sql="update GAME_PKG set REPLACE_PKG_ID=null where id=%s"%(newPkgId)
    cursor.execute(sql)
    conn.commit()


#�Ƴ������ظ��İ�
# pkgId : ����id
# gId : ��Ϸid
# md5 : �°���md5ֵ
def deleteDuplicatePkg(pkgId,gId,md5):
    
    #��1������ѯ�°��Ƿ���֮ǰ��Ϊmd5ֵ�ظ����Ѿ���ɾ���ˣ������ִ�����������
    #      ���ܵ��µĺ���ǣ�md5ֵ�ظ���2�����������ཫ�Է�ɾ����
    if checkPkgExist(pkgId) == False:
        #�°���Ϊmd5�ظ����Ѿ���ɾ����,ʲôҲ������ֱ�ӷ���
        return;
    
    #��2������ѯ��Ҫɾ���İ�id��2����ͬ����Ӫ��Ա�ϴ���ͬһ����Ϸ��ͬһ����(һģһ�����ļ���md5ֵ�ظ�,���丽���Ĺ���md5ֵ��ͬ)��
    sql="select concat('',id) from GAME_PKG where game_id=%s and id !=%s and  md5='%s' and (original_id is null or original_id='') union all select concat('',id) from GAME_PKG where game_id=%s and original_id in (select id from GAME_PKG where game_id=%s and id !=%s and  md5='%s' and (original_id is null or original_id=''))"%(gId,pkgId,md5,gId,gId,pkgId,md5)
    cursor.execute(sql)
    rs = cursor.fetchall()
    toDeleteIds="0"
    if len(rs) > 0:
        for row in rs:
            toDeleteIds = toDeleteIds + "," + row[0]
    
    #��3��������ص����ݼ�¼��GAME_PKG_HISTORY���У��Ա���ڵ�����һ��ʱ����ȴ�󣬴�cdnԴվ��ɾ����
    sql="insert into GAME_PKG_HISTORY(game_id,pkg_id,file_size,md5,package_name,version_name,created_by,version_code,url,created_date,publish_date) select game_id,id,file_size,md5,package_name,version_name,created_by,version_code,url,created_date,now() from GAME_PKG where id in (%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()

    #��4����ɾ����GAME_PKG_MANIFEST���ж�Ӧ������
    sql="delete from GAME_PKG_MANIFEST where pid in(%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()
    #��5����ɾ����GAME_PKG_CHANNEL���ж�Ӧ������
    sql="delete from GAME_PKG_CHANNEL where game_pkg_id in(%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()
    
    #��6����ɾ����GAME_PKG���ж�Ӧ������
    sql="delete from GAME_PKG where id in (%s)"%(toDeleteIds)
    cursor.execute(sql)
    conn.commit()


#�޸���Ϸ״̬
def changeSyncStatus():
    msgBody=""
    isNoticeWandoujia=False
    postUrls=""
    #��ѯû��ͬ����ɵķǹ���
    sql="select P.URL, P.FILE_SIZE, P.ID, P.GAME_ID, P.CREATED_DATE,P.REPLACE_PKG_ID,P.MD5,P.IS_DEFAULT from GAME_PKG P inner join GAME G on G.ID = P.GAME_ID where P.SYNC_STATUS = 0 and (P.ORIGINAL_ID IS NULL or P.ORIGINAL_ID='') and G.COPYRIGHT_TYPE = %s order by ID limit 20"%(COPYRIGHT_TYPE)
    cursor.execute(sql)
    rs1 = cursor.fetchall()  
    #print len(rs1)
    
    #ѭ�����еİ���Ȼ��ƴװ���ļ��ڸ���cdnԴվ�ϵĴ��̵�ַ
    for row1 in rs1:
        url=row1[0]
        pkgFileSize=long(row1[1])
        pkgId=row1[2]
        gId=row1[3]
        createdDate=time.strptime(str(row1[4]), "%Y-%m-%d %H:%M:%S")
        replacePkgId=row1[5]#���°�ʱ�����滻�ľɰ�id
        md5=row1[6]
        isDefault=row1[7]
        #print "gameId:%s pkgId:%s"%(gId, pkgId)
        if checkPkgExist(pkgId) == False:
            #�°���Ϊmd5�ظ����Ѿ���ɾ����,ʲôҲ������ֱ�ӽ�����һ��
            continue;
        
        syncFinish=checkSyncFinish(url,pkgFileSize,pkgId,gId,createdDate);
        
        if "yes" == syncFinish :
            #ͬ�����
            #����ж�Ӧ�Ĺ�����Ҫ��Ӧ�Ĺ���Ҳͬ����ɣ�����������ͬ�����
            sqlADV="select URL, FILE_SIZE, ID, GAME_ID, CREATED_DATE,REPLACE_PKG_ID,MD5 from GAME_PKG where ORIGINAL_ID=%s and SYNC_STATUS = 0  order by ID"%(pkgId)
            cursor.execute(sqlADV)
            rsADV = cursor.fetchall()
            
            advpkgSyncFinish=''
            if len(rsADV) > 0:
                #����й������������Ƿ�ͬ�����
                advpkgSyncFinish = checkSyncFinish(rsADV[0][0],rsADV[0][1],rsADV[0][2],rsADV[0][3],time.strptime(str(rsADV[0][4]), "%Y-%m-%d %H:%M:%S"))
                if "yes"==advpkgSyncFinish :
                    changeSyncFinishedStatus(rsADV[0][2])
                elif "no" != advpkgSyncFinish :
                    #ͬ��δ��ɣ����ҳ�ʱ��
                    msgBody = msgBody + advpkgSyncFinish
            else :
                #û�й���
                advpkgSyncFinish = "yes"
                
            if "yes"==advpkgSyncFinish :
                #������滻�ɰ���������滻�ɰ��������Ϣ
                if replacePkgId!=None and replacePkgId!='':
                    replaceOldPkgWithNew(pkgId,gId,md5,replacePkgId)
                #ɾ���ظ��İ���md5ֵ��ͬ��
                deleteDuplicatePkg(pkgId,gId,md5)
                #�����Ĭ�ϰ����򽫸���Ϸ��Ӧ��������ȫ������Ϊ��Ĭ�ϰ�
                if isDefault==1 :
                    sql="update GAME_PKG set is_default=0 where game_id=%s and id!=%s"%(gId,pkgId)
                    cursor.execute(sql)
                    conn.commit()
                #�޸��°���ͬ��״̬
                changeSyncFinishedStatus(pkgId)
                #���¶�Ӧ����Ϸ����Ϣ
                curDate = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                sql="update GAME set LATEST_VERSION_NAME=(select version_name from GAME_PKG where id=%s),LINKS=(select count(id) from GAME_PKG where game_id=%s and status=1 and sync_status=1),publish_date='%s',LAST_MODIFY_DATE='%s' where id=%s"%(pkgId,gId,row1[4],curDate,gId)
                cursor.execute(sql)
                conn.commit()
                activeMqConn.send({'GAME_CHANNEL_ID':101, 'GAME_ID':gId, 'PACKAGE_ID':pkgId}, destination='/topic/downjoy.android.jms.ResourceTopic', headers={'transformation' :'jms-map-json'}, ack='auto')
                #activeMqConn176.send({'t':'GAME', 'id':gId, 'm':'a', 's':'sync_python'}, destination='/topic/com.downjoy.android.jms.DROID_GAME_DATA_CHANGE', headers={'transformation' :'jms-map-json'}, ack='auto')
                #print "=============succeed================="
        elif "no" != syncFinish :
            #ͬ��δ��ɣ����ҳ�ʱ��
            msgBody = msgBody + syncFinish
    
    if msgBody != "" :
        sendmail('webmaster@downjoy.com', MONITOR_MAIL, msgBody, "android ͬ���ļ�����,211.147.5.167_usr_local_bin_new_changeAndroidGameStatus.py")
#��������Ƿ������У���������У�ֱ�ӷ���true��
#���û�����У����ļ��м�¼�ı�ʶλ��Ϊtrue��ͬʱ����false
def checkTaskRunning():
    f = file(SYNC_STATUS_FILE, "r")
    line = f.readline()
    f.close()
    if "true" == line:
        return True
    else :
        f = file(SYNC_STATUS_FILE, "w")
        f.write("true")
        f.close()
        return False
    
#�ű�ִ����ɺ���������״̬
def resetTaskStatus():
    f = file(SYNC_STATUS_FILE, "w")
    f.write("false")
    f.close()
        
startTime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
print "new_changeAndroidGameStatus.py start at %s"%startTime
try :
    taskRunning=checkTaskRunning()
    if taskRunning == False:
        conn = MySQLdb.connect(host="192.168.0.35", user="moster", passwd="shzygjrmdwg", db="droid_game")
        cursor = conn.cursor()
        activeMqConn = stomp.Connection(host_and_ports=[('192.168.0.148', 61613)])
        activeMqConn.start()
        activeMqConn.connect()
        activeMqConn176 = stomp.Connection(host_and_ports=[('192.168.0.176', 61613)])
        activeMqConn176.start()
        activeMqConn176.connect()
        
        getServerNodeChannelMap()
        getServerNodeUrlMap()
        getServerNodeInfos()
        changeSyncStatus()
        notifyCDN()
        
        #�ر�����
        activeMqConn.disconnect()
        activeMqConn176.disconnect()
        cursor.close()
        conn.close()
        
        #��������״̬
        resetTaskStatus()
    else :
        print "task already running,do nothing"
except Exception, ex:
    resetTaskStatus()
    
endTime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
print "new_changeAndroidGameStatus.py end at %s"%endTime

