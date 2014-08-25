#!/usr/bin/env python
#coding=utf-8
import sys, time, os
import db_connector
from django.core.mail import send_mail
from javalog.models import *
from javalog.comm import *

Javalog.objects.all().delete()
#开发环境
os.system("""awk '{$5="";print}' /opt/jiuxian-test/update/ceshi_common |egrep "^\w"|sed 's/.war//'|sed 's#/data/web/##' >kaifalist""")
#Javalog.objects.filter(idc='ceshi').delete()
f = open('kaifalist')
data = f.readlines()
f.close()
for i in data:
    L = i.strip().split()
    Javalog.objects.create(username=L[0],name=L[1],idc=L[2],ip=L[3],process=L[4],dir=L[5])

#测试环境和线上环境
os.system("""awk '{$5="";$8="";$9="";print}' online_common |egrep "^\w"|sed 's/.war//'|sed 's#/data/web/##' >wwwlist""")
#Javalog.objects.filter(idc='B28').delete()
#Javalog.objects.filter(idc='TJ').delete()
f = open('wwwlist')
data = f.readlines()
f.close()
for i in data:
    L = i.strip().split()
    Javalog.objects.create(username=L[0],name=L[1],idc=L[2],ip=L[3],process=L[4],dir=L[5])


sys.exit(0)

#redis
Redis.objects.all().delete()
f = open('redis_list')
data = f.readlines()
f.close()
for i in data:
    L = i.strip().split()
    Redis.objects.create(username=L[0],idc=L[1],ip=L[2])
