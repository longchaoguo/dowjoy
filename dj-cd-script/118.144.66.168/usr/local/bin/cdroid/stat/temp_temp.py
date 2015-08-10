#!/usr/bin/python
# -*- #coding:cp936

__author__ = "$Author: xiaodong.zheng$"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2013/10/29 09:09:22 $"
###########################################
import re
import urllib


###########################################
#获取日志产生时间
#line='2013-11-24 07:48:29@!@get@!@/misc/severmessages@!@{"resolutionWidth":444,"resolutionHeight":800,"osName":"4.0.3 JetROM","version":"6.4.1","clientChannelId":"100400","device":"G2","imei":"","hasRoot":"true","num":"null","sdk":15,"ss":3,"sswdp":640,"dd":120,"it":"2","verifyCode":"09e4669c66692eb10ef995ba457d76e3"}'
#pattern = re.compile("(?P<TIME>\S+)@\!@\S+@\!@\S+@\!@\S+")
#http://u.androidgame-store.com\/\w+\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")
#line = '<a href="http://android.d.cn/gameloft/" target="_blank"><img src="http://res.d.cn/android/new/news/201107/1309487638565kzLC.gif" style="-moz-box-shadow: 0pt 0pt 2px rgb(255, 255, 255); border: 0pt none;" alt="Gameloft 安卓游戏下载专区" /></a>'


#pattern=re.compile("^(?P<IP>\S*) \S* \S* \[(?P<TIME>\S*) \S*\] \S* (http:\/\/.*\.com)?\/[^\/]*\/[^\/]*\/game1\/[^\/]*\/(?P<GID>[^\/]*)\/\S* \S* (?P<STATUS>\S*) .* (?P<VERSION>\S*)\"$")


#\"verifyCode\":\"0774337b197fa8dcd7b3ae2da648d88d\",\"it\":\"2\",\"resolutionWidth\":320,\"imei\":\"867083017989516\",\"clientChannelId\":\"100400\",\"version\":\"6.6\",\"dd\":160,\"num\":\"null\",\"sswdp\":320,\"hasRoot\":\"true\",\"device\":\"ZTE_U790\",\"ss\":2,\"sdk\":10,\"resolutionHeight\":480,\"OsName\":\"2.3.6\",\"gpu\":\"PowerVR SGX 531\"



########################################################
def main():
    
    line = '116.207.240.235 - - [27/Apr/2014:00:02:07 +0800] "GET http://p.androidgame-store.com/new/game1/21/114321/titaniumbackup_1375768950314.apk HTTP/1.1" 200 6184679 "-" "LENOVO-Lenovo-A298t/1.0 Linux/2.6.35.7 Android 2.3.5 Release/11.22.2012 Browser/AppleWebKit533.1 (KHTML, like Gecko) Mozilla/5.0 Mobile"'
    patternWap = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://p.androidgame-store.com\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")

    pattern = re.compile("(?P<IP>\S*) \S* \S* \[(?P<TIME>\S+) \S+\] \S+ http://p.androidgame-store.com\/\w+\/(?P<GAME>\w+)\/\d+\/(?P<RID>\d+)\/(?P<PKG>\S*)\?f=(?P<PARAM>[^&=]*)\S* \S* (?P<STATUS>\d+) \S* \S* \"(?P<UA>[^\"]*)\"")

    #print line
    #line = line.replaceAll("\\","")
    match = pattern.match(line)
    if match:
        print "====1"
        #urlStr = match.group("URL")
        #if urlStr == '/dir/index-adv':
    wapMatch = patternWap.match(line)
    if wapMatch:
        print "======2"
        status = wapMatch.group('STATUS')
        game = wapMatch.group('GAME')
        ip = wapMatch.group('IP')
        recordTime = wapMatch.group('TIME')
        gameId = int(wapMatch.group('RID'))
        param = 'wap'
        pkgStr = wapMatch.group('PKG')
        print gameId
        if game == 'game1':
            gameId = gameId ^ 110111
        print gameId
            #print "-==1"
    #print match.group("IP")
    #headStr = "{"+match.group("HEAD").replace("\\", "")+"}"

    #print headStr


    #user=cdnpush&;password=cdn123!@#push&domain=p.androidgame-store.com&date=2013-12-17
    '''data = {}
    data['user'] = "cdnpush"
    data['password'] = "cdn123!@#push"
    data['date'] = "2013-12-17"
    data['domain'] = "p.androidgame-store.com"
    url = "http://runreport.dnion.com/DCC/logDownLoad.do?" + urllib.urlencode(data)
    print url
    rs = urllib.urlopen(url)
    print rs
    f = open("E://test.gz", 'wb')
    f.write(rs.read())
    f.close()
    rs.close()
    '''
    '''
    #pattern = re.compile(".*\<a href=\"http://android.d.cn\/(?P<URL>\w+)\/.*\".+\<img src=\"http://res.d.cn\/android\/new\/news\/201107\/1309487638565kzLC\.gif\".+\<\/a\>")
    #pattern = re.compile(".+num\":\"(?P<IMEI>15555215554)\")
    #line='2013-11-24 14:59:24@!@get@!@/dir/ranking/hot-game@!@{"resolutionWidth":540,"resolutionHeight":960,"osName":"4.1.2","version":"6.5.2","clientChannelId":"100454","device":"N:_T8950","imei":"+867495010631327","hasRoot":"true","num":"","sdk":16,"ss":2,"sswdp":360,"dd":240,"it":"2","verifyCode":"2565e28c7556d79a52f17d625d3b9eaa"}'
    linestr = ['2013-10-30 18:41:37@!@get@!@/item/12186_1@!@{"resolutionWidth":480.0,"resolutionHeight":800.0,"osName":"2.3.3","version":"5.9.5","clientChannelId":"100400","device":"sdk","imei":"717143544010679","hasRoot":"true","num":"15555215554","sdk":10.0,"ss":2.0,"sswdp":320.0,"dd":240.0,"it":"2","verifyCode":"9e0ea95bfde2ffa4290011cf0d9dc41a"}','2013-10-30 18:41:37@!@get@!@/dir/v4.7x/index-adv@!@{"resolutionWidth":720,"resolutionHeight":1280,"osName":"4.1.2","version":"5.4","clientChannelId":"100400","device":"GT-I9300","imei":"353921050098979","num":"","sdk":16,"it":"2","verifyCode":"dac839394418e73ba525add1762ba510"}','2013-10-30 18:41:37@!@get@!@/v64x/dir/index-adv@!@{"resolutionWidth":800,"resolutionHeight":1280,"osName":"4.2.2","version":"6.5.1","clientChannelId":"100400","device":"SM-T311","imei":"357397050308856","hasRoot":"false","num":"15555215554","sdk":17,"ss":3,"sswdp":600,"dd":213,"it":"2","verifyCode":"b9019393dc1ddbd445f7fc472f622cc0"}']
    #pattern = re.compile("(?P<TIME>\S{10} \S{8}).+clientChannelId\":\"(?P<CHANNEL_ID>\d+).+imei\":\"(?P<IMEI>\w*\_?\w*)")
    #match = pattern.match(line)
    #print match.group("TIME")
    #print match.group("CHANNEL_ID")
    #print match.group("IMEI")

    for i range 100:
        print str(i)
    channelPattern = re.compile(".+clientChannelId\":\"(?P<CHANNEL_ID>\d+)\"")
    imeiPattern = re.compile(".+imei\":\"(?P<IMEI>\w*\_?\w*)\"")
    numPattern = re.compile(".+num\":\"(?P<NUM>15555215554)\"")
    for line in linestr:
        line = line.strip()
        array = line.split('@!@')
        if len(array) != 4 or array[3] == 'null':
            #fw.write(line)
            #print line
            continue
        headArray = array[3].replace("{", "").replace("}", "").split(",")
        match1 = channelPattern.match(array[3])
        match2 = imeiPattern.match(array[3])
        match3 = numPattern.match(array[3])
        if match3:
            print "===="
            continue
        if not match1 or not match2:
            print line
            continue
        print match1.group("CHANNEL_ID")
        print match2.group("IMEI")
    '''
    '''
    headDict = {}
    for headstr in headArray:
        element = headstr.split('":')
        if len(element) > 1:
            headDict[element[0].replace('"', '')]=element[1].replace('"', '')
    print headDict
    createdDate = array[0]
    if not headDict.has_key("clientChannelId") or not headDict.has_key("imei"):
        print line
    clientChannelId = headDict["clientChannelId"]
    imei = headDict["imei"]
    print createdDate
    print clientChannelId
    print imei

    xxx = "1234|1234213|1234|1234|1234|43|"
    col = xxx.split("|")
    print len(col)
'''

main()



