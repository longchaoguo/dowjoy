import re
import os 
import sys
import fileinput
output=open(r'C:/Users/Administrator/Desktop/2.3output.txt','a')
sys.stdout=output
#读取日志

yxqd=[]
syd=[]
lbtd=[]
lbd=[]
sd=[]
dgd=[]

lines=fileinput.input(r'C:\Users\Administrator\Desktop\test.txt')

#/newdiguaserver/user/activity/follow
#/newdiguaserver/search/precise
#/newdiguaserver/game/index720
#/newdiguaserver/res/detail?homePage=gameList_1
# /newdiguaserver/res/detail?homePage=shufflingFigur
#/newdiguaserver/res/detail?homePage=singleGame
for line in lines:
   
    yxqs=re.compile("/newdiguaserver/user/activity/follow")
    syss=re.compile("/newdiguaserver/game/index720")
    lbts=re.compile("(/newdiguaserver/res/detail\s\?homePage=shufflingFigure_)(\d){1,2}")
    lbs=re.compile("(/newdiguaserver/res/detail\s\?homePage=gameList_)(\d){1,2}")
    ss=re.compile("/newdiguaserver/search/precise")
    dgs=re.compile("(/newdiguaserver/res/detail\s\?homePage=singleGame_)(\d){1,2}")
    search1=yxqs.search(line)
    search2=syss.search(line)
    search3=lbts.search(line)
    search4=lbs.search(line)
    search5=ss.search(line)
    search6=dgs.search(line)
    if search1:
        yxq = search1.group(0)
        #cont=cont+ip.count('"- "')
        yxqd.append(yxq)
        #yxqf=tuple(arr)
    if search2:
        sy=search2.group(0)
        syd.append(sy)
    if search3:
        lbt=search3.group(0)
        lbtd.append(lbt)
    if search4:
        lb=search4.group(0)
        lbd.append(lb)
    if search5:
        s=search5.group(0)
        sd.append(s)
    if search6:
        dg=search6.group(0)
        dgd.append(dg)
print ("游戏圈总访问pv: %d" % len(yxqd))
print ("首页总访问pv: %d" % len(syd))
print ("轮播图总访问pv: %d" % len(lbtd))
print ("游戏列表总访问pv: %d" % len(lbd))
print ("搜索总访问pv: %d" % len(sd))
print ("单个游戏总访问pv: %d" % len(dgd))

sys.stdout=sys.__stdout__
output.close()
