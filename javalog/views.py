#!/usr/bin/env python
#coding=utf-8
#author: hhr
import time,datetime,os,sys,re
import random
import paramiko
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.contrib.auth.models import User
from django.template import RequestContext
import db_connector
from javalog.models import *
from javalog.form import *
from javalog.comm import *
from django.utils import simplejson
reload(sys)   
sys.setdefaultencoding('utf8')

#超级管理员
super = ['root','hhr']
#前台按钮显示控制,
showroot = ['test']
showroot.extend(super)
#后台执行权限控制，超级管理员无需设置，格式：用户_机房
execroot = ['test_ceshi']
testpasswd = Passwd.objects.filter(name="test")[0].passwd
onlinepasswd = Passwd.objects.filter(name="online")[0].passwd
def index(request):
    if str(request.user) != "AnonymousUser":
        user = request.user
        if str(user) in showroot:
            show = "ok"
        return render_to_response('index.html',locals())
    else:
        return HttpResponseRedirect('/login/')

def account_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = request.user
    login_err = "对不起，用户名或密码不对！"
    user = auth.authenticate(username=username,password=password)
    if user is not None:
        auth.login(request,user)
        return HttpResponseRedirect('/javalog/')
    else:
        return render_to_response('login.html',locals())

def login(request):
    user = request.user
    return render_to_response('login.html',locals())

def logout(request):
    user = request.user
    auth.logout(request)
    return HttpResponseRedirect('/login/')

#java日志查看
@login_required
def javalog(request):
    user = request.user
    names = [row.name for row in Javalog.objects.filter(username=user)]
    if str(user) in showroot:
        names = [row.name for row in Javalog.objects.all()]
        show = 'ok'
    names = sorted(list(set(names)))
    num = 150
    return render_to_response('javalog.html',locals())
def getIdc(request):
    user = request.user
    name = request.GET.get('name')
    idcs = [row.idc for row in Javalog.objects.filter(username=str(user),name=name)]
    if str(user) in showroot:
        idcs = [row.idc for row in Javalog.objects.filter(name=name)]
    idcs = list(set(idcs))
    json = simplejson.dumps(idcs)
    return HttpResponse(json)
def getIp(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ips = [("%s_%s" % (row.ip,row.dir)) for row in Javalog.objects.filter(username=str(user),name=name,idc=idc)]
    if str(user) in showroot:
        ips = [("%s_%s" % (row.ip,row.dir)) for row in Javalog.objects.filter(name=name,idc=idc)]
    json = simplejson.dumps(ips)
    return HttpResponse(json)
def getFile(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ipdir = request.GET.get('ipdir')
    dir = ipdir.split('_')[1]
    ip = ipdir.split('_')[0]
    dirtype = request.GET.get('dirtype')
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if dirtype == 'tomcat':
            cmd = 'ls /log/web/%s' % dir
            files = ssh(ip,passwd,cmd)[ip].split('\n')
    if dirtype == 'services':
        cmd = 'cd /log/web/service ; ls %s*' % name
        files = ssh(ip,passwd,cmd)[ip].split('\n')
    if dirtype == '':
        files = []
    json = simplejson.dumps(files)
    return HttpResponse(json)
def showLog(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ipdir = request.GET.get('ipdir')
    dir = ipdir.split('_')[1]
    ip = ipdir.split('_')[0]
    dirtype = request.GET.get('dirtype')
    file = request.GET.get('file')
    num = request.GET.get('num')
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if dirtype == 'tomcat':
        if file.endswith('.gz'):
            cmd = 'zcat /log/web/%s/%s|tail -n %s' % (dir,file,num)
        else:
            cmd = 'tail -n %s /log/web/%s/%s' % (num,dir,file)
    if dirtype == 'services':
        if file.endswith('.gz'):
            cmd = 'zcat /log/web/service/%s|tail -n %s' % (file,num)
        else:
            cmd = 'tail -n %s /log/web/service/%s' % (num,file)
    datas = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(datas)
    return HttpResponse(json)
def restart(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ipdir = request.GET.get('ipdir')
    dir = ipdir.split('_')[1]
    ip = ipdir.split('_')[0]
    cmd = 'sudo sh /data/bin/tomcat.sh restart  %s' % dir
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        datas = ssh(ip,passwd,cmd)[ip]
    else:
        datas = "用户权限不够，无法重启！"
    json = simplejson.dumps(datas)
    return HttpResponse(json)
def stop(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ipdir = request.GET.get('ipdir')
    dir = ipdir.split('_')[1]
    ip = ipdir.split('_')[0]
    cmd = 'sudo sh /data/bin/tomcat.sh stop %s' % dir
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        datas = ssh(ip,passwd,cmd)[ip]
    else:
        datas = "用户权限不够，无法停止！"
    json = simplejson.dumps(datas)
    return HttpResponse(json)
def status(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ipdir = request.GET.get('ipdir')
    dir = ipdir.split('_')[1]
    ip = ipdir.split('_')[0]
    cmd = 'sudo sh /data/bin/tomcat.sh status %s' % dir
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(datas)
    return HttpResponse(json)
def down(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ipdir = request.GET.get('ipdir')
    dir = ipdir.split('_')[1]
    ip = ipdir.split('_')[0]
    dirtype = request.GET.get('dirtype')
    file = request.GET.get('file')
    if dirtype == 'tomcat':
            f = '/log/web/%s/%s' % (dir,file)
    if dirtype == 'services':
        f = '/log/web/service/%s' % file
    if idc == 'ceshi':
        mip = '192.168.6.30'
        passwd = 'jiuxian2014'
        if file.endswith('gz'):
            cmd = "ls /data/download/|grep %s" % file
            ret = ssh(mip,passwd,cmd)[mip].strip('\n')
            if file == ret:
                json = simplejson.dumps('ok')
            else:
                cmd = "sudo rcp %s:%s /data/download/%s_%s;echo 'ok'" % (ip,f,ipdir,file)
                ret = ssh(mip,passwd,cmd)[mip].strip('\n')
                json = simplejson.dumps(ret)
        else:
            cmd = "sudo rcp %s:%s /data/download/%s_%s;echo 'ok'" % (ip,f,ipdir,file)
            ret = ssh(mip,passwd,cmd)[mip].strip('\n')
            json = simplejson.dumps(ret)
    else:
        mip = '192.168.10.249'
        passwd = onlinepasswd
        if file.endswith('gz'):
            cmd = "ls /data/download/|grep %s" % file
            ret = ssh(mip,passwd,cmd)[mip].strip('\n')
            if file == ret:
                json = simplejson.dumps('ok')
            else:
                cmd = "sudo rcp %s:%s /data/download/%s_%s;echo 'ok'" % (ip,f,ipdir,file)
                ret = ssh(mip,passwd,cmd)[mip].strip('\n')
                json = simplejson.dumps(ret)
        else:
            cmd = "sudo rcp %s:%s /data/download/%s_%s;echo 'ok'" % (ip,f,ipdir,file)
            ret = ssh(mip,passwd,cmd)[mip].strip('\n')
            json = simplejson.dumps(ret)
    return HttpResponse(json)

#redis配置文件查看
@login_required
def redis(request):
    user = request.user
    idcs = [row.idc for row in Redis.objects.all()]
    idcs = sorted(list(set(idcs)))
    if str(user) in showroot:
        show = 'ok'
    return render_to_response('redis.html',locals())
def redisgetip(request):
    user = request.user
    idc = request.GET.get('idc')
    ips = [row.ip for row in Redis.objects.filter(idc=idc)]
    ips = sorted(list(set(ips)))
    json = simplejson.dumps(ips)
    return HttpResponse(json)

def redisgetfile(request):
    user = request.user
    idc = request.GET.get('idc')
    ip = request.GET.get('ip')
    cmd = 'ls /etc/redis'
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    files = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(files)
    return HttpResponse(json)
def redisview(request):
    user = request.user
    idc = request.GET.get('idc')
    ip = request.GET.get('ip')
    file = request.GET.get('file')
    cmd = 'cat /etc/redis/%s' % file
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip]
    json = simplejson.dumps(datas)
    return HttpResponse(json)

def redisedit(request):
    user = request.user
    idc = request.POST.get('idc')
    ip = request.POST.get('ip')
    file = request.POST.get('file')
    data = request.POST.get('data')
    cmd = 'echo "%s" |sudo tee /etc/redis/%s &&echo edit ok' % (data,file)
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        ret = ssh(ip,passwd,cmd)[ip]
        if 'edit ok' in ret:
            ret = "修改成功!"
    else:
        ret = "用户权限不够，无法修改!"
    return HttpResponse(ret)

def redisstatus(request):
    user = request.user
    idc = request.POST.get('idc')
    ip = request.POST.get('ip')
    file = request.POST.get('file')
    port = re.search("(\d+)",file).group()
    cmd = '/usr/local/bin/redis-cli -p %s info' % port
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip]
    return HttpResponse(datas)

def redisrestart(request):
    user = request.user
    idc = request.POST.get('idc')
    ip = request.POST.get('ip')
    file = request.POST.get('file')
    port = re.search("(\d+)",file).group()
    datas = ""
    cmd = 'sudo sh /data/bin/redis.sh restart %s' % port 
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        datas = ssh(ip,passwd,cmd)[ip]
    else:
        datas = "用户权限不够，无法重启！"
    return HttpResponse(datas)

@login_required
def zookeeper(request):
    user = request.user
    idcs = [row.idc for row in Zookeeper.objects.all()]
    idcs = sorted(list(set(idcs)))
    if str(user) in showroot:
        show = 'ok'
    return render_to_response('zookeeper.html',locals())
def zookeepergetip(request):
    user = request.user
    idc = request.GET.get('idc')
    ips = [row.ip for row in Zookeeper.objects.filter(idc=idc)]
    ips = sorted(list(set(ips)))
    json = simplejson.dumps(ips)
    return HttpResponse(json)

def zookeepergetfile(request):
    user = request.user
    idc = request.GET.get('idc')
    ip = request.GET.get('ip')
    cmd = 'ls /usr/local/zookeeper/zk/conf'
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    files = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(files)
    return HttpResponse(json)

def zookeeperview(request):
    user = request.user
    idc = request.GET.get('idc')
    ip = request.GET.get('ip')
    file = request.GET.get('file')
    cmd = 'cat /usr/local/zookeeper/zk/conf/%s' % file
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip]
    json = simplejson.dumps(datas)
    return HttpResponse(json)

def zookeeperedit(request):
    user = request.user
    idc = request.POST.get('idc')
    ip = request.POST.get('ip')
    file = request.POST.get('file')
    data = request.POST.get('data')
    cmd = 'echo "%s" |sudo tee /usr/local/zookeeper/zk/conf/%s &&echo edit ok' % (data,file)
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        ret = ssh(ip,passwd,cmd)[ip]
        if 'edit ok' in ret:
            ret = "修改成功！"
    else:
        ret = "用户权限不够，无法修改！"
    return HttpResponse(ret)

def zookeeperstatus(request):
    user = request.user
    idc = request.POST.get('idc')
    ip = request.POST.get('ip')
    cmd = 'sudo /usr/local/zookeeper/zk/bin/zkServer.sh status'
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip]
    return HttpResponse(datas)
def zookeeperrestart(request):
    user = request.user
    idc = request.POST.get('idc')
    ip = request.POST.get('ip')
    cmd = 'sudo /usr/local/zookeeper/zk/bin/zkServer.sh  restart' 
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        datas = ssh(ip,passwd,cmd)[ip]
    else:
        datas = "用户权限不够，无法重启！"
    return HttpResponse(datas)

#war包和公共jar包下载
@login_required
def downwar(request):
    user = request.user
    names = [row.name for row in Javalog.objects.filter(username=user)]
    if str(user) in showroot:
        show = "ok"
        names = [row.name for row in Javalog.objects.all()]
    names = sorted(list(set(names)))
    return render_to_response('downwar.html',locals())
def war(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ip = Javalog.objects.filter(name=name,idc=idc)[0].ip
    dir = Javalog.objects.filter(name=name,idc=idc,ip=ip)[0].dir
    if idc == 'ceshi':
        passwd = testpasswd
        warname = "%s.war" % name
        f = "/data/web/%s/%s" % (dir,warname)
        t = paramiko.Transport((ip,9830))
        t.connect(username='jiuxian',password=passwd)
        sftp=paramiko.SFTPClient.from_transport(t)
        sftp.get(f,'/data/download/%s' % warname)
        json = simplejson.dumps(warname)
        return HttpResponse(json)
    else:
        passwd = onlinepasswd
    if name == "mobileservices":
        json = simplejson.dumps('false')
        return HttpResponse(json)   
    warname = "%s.war" % name
    md5cmd = "md5sum `ls -rt /data/update/backup/bak_online_war/www_after/%s/*/%s.war|tail -n1`" % (idc,name)
    md5cmd1 = "md5sum /data/web/%s/%s" % (dir,warname)
    mip = "192.168.10.249"
    m = ssh(mip,passwd,md5cmd)[mip]
    m1= ssh(ip,passwd,md5cmd1)[ip]
    if m.split()[0] == m1.split()[0]:
        f = m.split()[1]
        cmd = "cp %s /data/download/"
        ret = ssh(mip,passwd,cmd)[mip]
        #f = f.lstrip("/data/update/backup/bak_online_war/www_after/") 
        json = simplejson.dumps(warname)
    else:
        json = simplejson.dumps('false')
    return HttpResponse(json)
def jar(request):
    user = request.user
    jarname = request.GET.get('jarname')
    idc1 = request.GET.get('idc1')
    if idc1 == 'ceshi':
        ip = "192.168.6.16"     #测试后台
        passwd = testpasswd
        #f = os.popen("ls -rt /data/update/backup/bak_jar_ceshi/www_after/ceshi/*/java_jar/JXConfig.jar|tail -n1")
    if idc1 == 'B28' or idc1 == PRE:
        ip = "192.168.10.162"   #线上后台
        passwd = onlinepasswd
    if idc1 == 'TJ':
        ip = '10.20.3.48'
        passwd = onlinepasswd
    f = "/data/web/java_jar/%s" % jarname
    t = paramiko.Transport((ip,9830))
    t.connect(username='jiuxian',password=passwd)
    sftp=paramiko.SFTPClient.from_transport(t)
    sftp.get(f,'/data/download/%s' % jarname)
    json = simplejson.dumps(jarname)
    return HttpResponse(json)        

@login_required
def hosts(request):
    user = request.user
    idcs = ['B28','PRE','TJ','ceshi']
    if str(user) in showroot:
        show = "ok"
    return render_to_response('hosts.html',locals())
def showhosts(request):
    user = request.user
    idc = request.GET.get('idc',)
    passwd = onlinepasswd
    mip = "192.168.10.249"
    cmd = "cat /opt/jiuxian/common/host_tab/%s.hosts" % idc
    if idc == "ceshi":
        ret = os.popen("cat /opt/jiuxian-test/common/host_tab/ceshi.hosts").read()
    else:
        ret = ssh(mip,passwd,cmd)[mip]
    json = simplejson.dumps(ret)
    return HttpResponse(json)
def hostedit(request):
    user = request.user
    idc = request.POST.get('idc')
    data = request.POST.get('data')
    ret = ""
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        if idc == 'ceshi':
            mip = "192.168.6.30"
            cmd = 'echo "%s" |sudo tee /opt/jiuxian-test/common/host_tab/ceshi.hosts &&echo edit ok' % data
            #passwd = testpasswd
            passwd = "jiuxian2014"
            ret = ssh(mip,passwd,cmd)[mip]
        else:
            mip = "192.168.10.249"
            passwd = onlinepasswd
            cmd = 'echo "%s" |sudo tee /opt/jiuxian/common/host_tab/%s.hosts &&echo edit ok' % (data,idc)
            ret = ssh(mip,passwd,cmd)[mip]
        if 'edit ok' in ret:
            ret = "修改成功！"
    else:
        ret = "用户权限不够，无法修改！"
    return HttpResponse(ret)
def hostsync(request):
    user = request.user
    idc = request.POST.get('idc')
    if "%s_%s" % (str(user),idc) in execroot or str(user) in super:
        if idc == "ceshi":
            ret = os.popen("sh /opt/jiuxian-test/update/jiuxian_ip_ceshi_update.sh uphosts www ceshi").read()
    else:
        ret = "用户权限不够，无法推送！"
    return HttpResponse(ret)

@login_required
def cdn(request):
    user = request.user  
    if str(user) not in super:
        return HttpResponseRedirect('/javalog/')
    show = 'ok'
    sites = [row.site for row in Cdnlog.objects.all()]
    sites = sorted(list(set(sites)),reverse=True)
    return render_to_response('cdnlog.html',locals())
def getDays(request):
    user = request.user
    site = request.GET.get('site')
    cdn = request.GET.get('cdn')
    days = request.GET.get('days')
    ret = []
    ret1 = []
    ret2 = []
    if days:
        days = int(days) 
        ds = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
        days =  [row.day for row in Cdnlog.objects.filter(day__gte=ds)]
        days = sorted(list(set(days)))
        cdns = [row.cdn for row in Cdnlog.objects.filter(site=site)]
        cdns = sorted(list(set(cdns)))
        for cdn in cdns:
            hits = []
            sizes = []
            bads = []
            for day in days:
                try:
                    hit = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].hit
                except:
                    hit = "0"
                try:
                    size = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].size
                except:
                    size = "0"
                try:
                    bad = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].bad
                except:
                    bad = "0"
                hits.append(hit)
                sizes.append(size)
                bads.append(bad)
            #颜色随机
            #r = hex(random.randint(0,255))[2:]
            #if len(r) == 1: r = "0" + r
            #g = hex(random.randint(0,255))[2:]
            #if len(g) == 1: g = "0" + g
            #b = hex(random.randint(0,255))[2:]
            #if len(b) == 1: b = "0" + b
            #color = "#%s%s%s" %(r,g,b)
            if cdn == "lx":
                cdn = "蓝汛"
                color = '#76a871'
            if cdn == "ws":
                cdn = "网宿"
                color = '#4572a7'
            if cdn == "sh":
                cdn = "搜狐"
                color = '#80699b'
            d = {'name':cdn,'value':hits,'color':color}    
            d1 = {'name':cdn,'value':sizes,'color':color}
            d2 = {'name':cdn,'value':bads,'color':color}
            ret.append(d)
            ret1.append(d1)
            ret2.append(d2)
    obj = {
        "hit":ret,
        "pv":ret1,
        "bad":ret2,
        "detail":"",
        "label":days
        }
    json = simplejson.dumps(obj)
    return HttpResponse(json)    
def getCdn(request):
    user = request.user
    site = request.GET.get('site')
    cdn = request.GET.get('cdn')
    days = request.GET.get('days')
    ret = []
    ret1 = []
    ret2 = []
    ret3 = []
    rets = []
    if cdn == "lx":
        color = '#76a871'
    if cdn == "ws":
        color = '#4572a7'
    if cdn == "sh":
        color = '#80699b'
    if days:
        days = int(days)
        ds = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
        days =  [row.day for row in Cdnlog.objects.filter(day__gte=ds)]
        days = sorted(list(set(days)))
        for day in days:
            try:
                hit = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].hit
            except:
                hit = "0"
            try:
                size = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].size
            except:
                size = "0"
            try:
                bad = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].bad
            except:
                bad = "0"
            d = {'name':day,'value':hit,'color':color}
            d1 = {'name':day,'value':size,'color':color}
            d2 = {'name':day,'value':bad,'color':color}
            ret.append(d)
            ret1.append(d1)
            ret2.append(d2)

    obj = {
        "hit":ret,
        "pv":ret1,
        "bad":ret2,
        "detail":"",
        "label":days,
        "cdn":cdn
        }
    json = simplejson.dumps(obj)
    return HttpResponse(json)
def getDay(request):
    user = request.user
    site = request.GET.get('site')
    cdn = request.GET.get('cdn')
    day = request.GET.get('day')
    ret = []
    ret1 = []
    ret2 = []
    hit = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].hit
    miss = 100 - float(hit.strip("%"))
    size = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].size
    bad = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].bad
    detail = Cdnlog.objects.filter(site=site,cdn=cdn,day=day)[0].detail
    ret = [{'name':"hit",'value':hit,'color':"#76a871"},{'name':"miss",'value':miss,'color':"#c12c44"}]
    ret1 = [{'name':"size",'value':size,'color':"#a5c2d5"}]
    ret2 = [{'name':"bad",'value':bad,'color':"#a5c2d5"}]
    obj = {
        "hit":sorted(ret),
        "pv":sorted(ret1),
        "bad":sorted(ret2),
        "detail":detail
        }
    json = simplejson.dumps(obj)
    return HttpResponse(json)

@login_required
def dblog(request):
    user = request.user
    if str(user) in showroot:
        show = 'ok'
    dbnames = [row.dbname for row in Dblog.objects.all()]
    dbnames = sorted(list(set(dbnames)))
    num = 50
    return render_to_response('dblog.html',locals())
def getDbip(request):
    user = request.user
    dbname = request.GET.get('dbname')
    ips = [row.ip for row in Dblog.objects.filter(dbname=dbname)]
    json = simplejson.dumps(ips)
    return HttpResponse(json)
def getDbfile(request):
    user = request.user
    dbname = request.GET.get('dbname')
    ip = request.GET.get('ip')
    file = request.GET.get('file')
    num = request.GET.get('num')
    passwd = onlinepasswd
    cmd = 'cd /my/log/;ls mysql.err*'
    files = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(files)
    return HttpResponse(json)
def showDblog(request):
    user = request.user
    dbname = request.GET.get('dbname')
    ip = request.GET.get('ip')
    file = request.GET.get('file')
    num = request.GET.get('num')
    passwd = onlinepasswd
    if file.endswith('.gz'):
        cmd = 'zcat /my/log/%s|tail -n %s' % (file,num)
    else:
        cmd = 'tail -n %s /my/log/%s' % (num,file)
    datas = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(datas)    
    return HttpResponse(json)
def downDblog(request):
    user = request.user
    dbname = request.GET.get('dbname')
    ip = request.GET.get('ip')
    file = request.GET.get('file')
    rnum = request.GET.get('rnum')
    passwd = onlinepasswd
    f = '/my/log/%s' % file
    sizecmd = 'du -sm %s' % f
    logsize = int(ssh(ip,passwd,sizecmd)[ip].split()[0])
    if logsize < 20:
        file = rnum + "_" + file
        t = paramiko.Transport((ip,9830))
        t.connect(username='jiuxian',password=passwd)
        sftp=paramiko.SFTPClient.from_transport(t)
        sftp.get(f,'/data/download/%s' % file)
        json = simplejson.dumps('ok')
    else:
        json = simplejson.dumps('false')
    return HttpResponse(json)

@login_required
def files(request):
    user = request.user
    if str(user) in super:
        show = "ok"
    if request.method == 'POST':
        upform = upfileForm(request.POST,request.FILES)
        if upform.is_valid():
            if upform.cleaned_data['file'].size > 5000000:
                ret = "File size no larger than 5M ,Upload Fail !!!"
            else:
                fp = file("/data/download/files/" + upform.cleaned_data['file'].name,'wb')
                for chunk in upform.cleaned_data['file'].chunks():
                    fp.write(chunk)
                fp.close()
                ret = "上传成功!"
    files = os.listdir("/data/download/files/")
    return render_to_response('files.html',locals())
def showFile(request):
    user = request.user
    files = request.GET.get('files',)
    f = open('/data/download/files/%s' % files)
    data = f.readlines()
    f.close()
    json = simplejson.dumps(data)
    return HttpResponse(json)
def editFile(request):
    user = request.user
    ret = ""
    if str(user) in super:
        files = request.POST.get('files')
        data = request.POST.get('data')
        if files:
            f = file('/data/download/files/%s' % files,'wb')
            f.write(data)
            f.close()
            ret = "修改成功！"
    return HttpResponse(ret)
def delFile(request):
    user = request.user
    files = request.GET.get('files')
    data = {}
    if str(user) in super:
        if files:
            os.remove('/data/download/files/%s' % files)
            data["ret"] = "删除成功！"
            data["files"] = os.listdir("/data/download/files/")
    json = simplejson.dumps(data)
    return HttpResponse(json)
