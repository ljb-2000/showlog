#!/usr/bin/env python
#coding=utf-8
import sys, time, os
import db_connector
from django.core.mail import send_mail
from javalog.models import *
from javalog.comm import *

#online_common文件格式
'''
#工程类别  WAR包                        机房  IP                中间件     进程                    online工程目录
mobile     mobileservices.war           B28   192.168.10.232    tomcat     tomcat1                 /data/web/tomcat1
www        JXService-Messenger.war      B28   192.168.10.217    tomcat     tomcat5-messenger       /data/web/tomcat5
'''
#redis_list文件格式
'''
www B28 192.168.10.108
'''
#Javalog.objects.all().delete()
#测试环境
def ceshijavaUpdate():
    os.system("""awk '{$5="";print}' /opt/jiuxian-test/update/ceshi_common |egrep "^\w"|sed 's/.war//'|sed 's#/data/web/##' >/data/download/lists/kaifalist""")
    Javalog.objects.filter(idc='ceshi').delete()
    f = open('/data/download/lists/kaifalist')
    data = f.readlines()
    f.close()
    for i in data:
        L = i.strip().split()
        Javalog.objects.create(username=L[0],name=L[1],idc=L[2],ip=L[3],process=L[4],dir=L[5])

#测试环境和线上环境
def javaUpdate():
    os.system("""awk '{$5="";$8="";$9="";print}' /data/download/lists/online_common |egrep "^\w"|sed 's/.war//'|sed 's#/data/web/##' >/data/download/lists/wwwlist""")
    Javalog.objects.filter(idc='B28').delete()
    Javalog.objects.filter(idc='TJ').delete()
    Javalog.objects.filter(idc='PRE').delete()
    f = open('/data/download/lists/wwwlist')
    data = f.readlines()
    f.close()
    for i in data:
        L = i.strip().split()
        Javalog.objects.create(username=L[0],name=L[1],idc=L[2],ip=L[3],process=L[4],dir=L[5])

#redis
def redisUpdate():
    Redis.objects.all().delete()
    f = open('/data/download/lists/redis_list')
    data = f.readlines()
    f.close()
    for i in data:
        L = i.strip().split()
        Redis.objects.create(username=L[0],idc=L[1],ip=L[2])

#redisUpdate()
#kfjavaUpdate()
javaUpdate()
ceshijavaUpdate()

