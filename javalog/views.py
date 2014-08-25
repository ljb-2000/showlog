#!/usr/bin/env python
#coding=utf-8
#author: hhr
import time,datetime,os,re
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
from javalog.comm import *
from django.utils import simplejson

testpasswd = Passwd.objects.filter(name="test")[0].passwd
onlinepasswd = Passwd.objects.filter(name="online")[0].passwd
def index(request):
    if str(request.user) != "AnonymousUser":
        user = request.user
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

def getIdc(request):
    user = request.user
    name = request.GET.get('name')
    idcs = [row.idc for row in Javalog.objects.filter(name=name)]
    idcs = list(set(idcs))
    json = simplejson.dumps(idcs)
    return HttpResponse(json)
def getIp(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    #ips = [row.ip for row in Javalog.objects.filter(name=name,idc=idc)]
    #ips = sorted(list(set(ips)))
    ips = [("%s_%s" % (row.ip,row.dir)) for row in Javalog.objects.filter(name=name,idc=idc)]
    json = simplejson.dumps(ips)
    return HttpResponse(json)
def getFile(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ip = request.GET.get('ip')
    dir = ip.split('_')[1]
    ip = ip.split('_')[0]
    dirtype = request.GET.get('dirtype')
    #dir = Javalog.objects.filter(name=name,idc=idc,ip=ip)[0].dir
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
    ip = request.GET.get('ip')
    dir = ip.split('_')[1]
    ip = ip.split('_')[0]
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
        #if str(user) == "mobile":
        #    cmd = 'tail -n %s /usr/local/%s/logs/%s' % (num,dir,file)
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
    ip = request.GET.get('ip')
    dir = ip.split('_')[1]
    ip = ip.split('_')[0]
    #process = Javalog.objects.filter(name=name,idc=idc,ip=ip,dir=dir)[0].process
    cmd = 'sudo sh /data/bin/tomcat.sh restart  %s' % dir
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(datas)
    return HttpResponse(json)
def stop(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ip = request.GET.get('ip')
    dir = ip.split('_')[1]
    ip = ip.split('_')[0]
    #process = Javalog.objects.filter(name=name,idc=idc,ip=ip,dir=dir)[0].process
    cmd = 'sudo sh /data/bin/tomcat.sh stop %s' % dir
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip].split('\n')
    json = simplejson.dumps(datas)
    return HttpResponse(json)
def status(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ip = request.GET.get('ip')
    dir = ip.split('_')[1]
    ip = ip.split('_')[0]
    #process = Javalog.objects.filter(name=name,idc=idc,ip=ip,dir=dir)[0].process
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
    ip = request.GET.get('ip')
    dir = ip.split('_')[1]
    ip = ip.split('_')[0]
    dirtype = request.GET.get('dirtype')
    file = request.GET.get('file')
    rnum = request.GET.get('rnum')
    if idc == 'ceshi':
        passwd = Passwd.objects.filter(name="test")[0].passwd
    else:
        passwd = Passwd.objects.filter(name="online")[0].passwd
    if dirtype == 'tomcat':
            f = '/log/web/%s/%s' % (dir,file)
    if dirtype == 'services':
        f = '/log/web/service/%s' % file
    sizecmd = 'du -sm %s' % f
    logsize = int(ssh(ip,passwd,sizecmd)[ip].split()[0])
    if logsize < 20:
        file = rnum + "_" + file
        t = paramiko.Transport((ip,9830))
        t.connect(username='jiuxian',password=passwd)
        sftp=paramiko.SFTPClient.from_transport(t)
        sftp.get(f,'/data/javalog/javalog/static/down/%s' % file)
        json = simplejson.dumps('ok')
    else:
        json = simplejson.dumps('false')
    return HttpResponse(json)

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
        passwd = Passwd.objects.filter(name="test")[0].passwd
    else:
        passwd = Passwd.objects.filter(name="online")[0].passwd
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
    ret = ssh(ip,passwd,cmd)[ip]
    if 'edit ok' in ret:
        ret = "修改成功！"
    #json = simplejson.dumps(ret)
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
    cmd = 'sudo sh /data/bin/redis.sh restart %s' % port 
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    datas = ssh(ip,passwd,cmd)[ip]
    return HttpResponse(datas)

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
    ret = ssh(ip,passwd,cmd)[ip]
    if 'edit ok' in ret:
        ret = "修改成功！"
    #json = simplejson.dumps(ret)
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
    #json = simplejson.dumps(datas)
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
    datas = ssh(ip,passwd,cmd)[ip]
    return HttpResponse(datas)

def war(request):
    user = request.user
    name = request.GET.get('name')
    idc = request.GET.get('idc')
    ip = Javalog.objects.filter(name=name,idc=idc)[0].ip
    dir = Javalog.objects.filter(name=name,idc=idc,ip=ip)[0].dir
    if idc == 'ceshi':
        passwd = testpasswd
    else:
        passwd = onlinepasswd
    if name == "mobileservices":
        json = simplejson.dumps('false')
        return HttpResponse(json)
    md5cmd = "md5sum `ls -rt /data/update/backup/bak_online_war/www_after/%s/*/%s.war|tail -n1`" % (idc,name)
    md5cmd1 = "md5sum /data/web/%s/%s.war" % (dir,name)
    m = ssh("192.168.10.249",passwd,md5cmd)["192.168.10.249"]
    m1= ssh(ip,passwd,md5cmd1)[ip]
    if m.split()[0] == m1.split()[0]:
        #f = m.split()[1]
        f = m.split()[1]
        f = f.lstrip("/data/update/backup/bak_online_war/www_after/") 
#        t = paramiko.Transport(("192.168.10.249",9830))
#        t.connect(username='jiuxian',password=passwd)
#        sftp=paramiko.SFTPClient.from_transport(t)
#        sftp.get(f,'/data/javalog/javalog/static/down/%s.war' % name)
        json = simplejson.dumps(f)
    else:
        json = simplejson.dumps('false')
    return HttpResponse(json)

@login_required
def javalog(request):
    user = request.user
    names = [row.name for row in Javalog.objects.filter(username=user)]
    if str(user) == 'root' or str(user) == 'test':
        names = [row.name for row in Javalog.objects.all()]
    names = sorted(list(set(names)))
    name = request.GET.get('name',)
    idc = request.GET.get('idc',)
    ip = request.GET.get('ip',)
    num = request.GET.get('num',)
    if not num:
        num = 150
    return render_to_response('javalog.html',locals())

@login_required
def redis(request):
    user = request.user
    idcs = [row.idc for row in Redis.objects.all()]
    idcs = sorted(list(set(idcs)))
    idc = request.GET.get('idc',)
    ip = request.GET.get('ip',)
    file = request.GET.get('file',)
    return render_to_response('redis.html',locals())
@login_required
def zookeeper(request):
    user = request.user
    idcs = [row.idc for row in Zookeeper.objects.all()]
    idcs = sorted(list(set(idcs)))
    idc = request.GET.get('idc',)
    ip = request.GET.get('ip',)
    file = request.GET.get('file',)
    return render_to_response('zookeeper.html',locals())
@login_required
def downwar(request):
    user = request.user
    names = [row.name for row in Javalog.objects.filter(username=user)]
    if str(user) == 'root' or str(user) == 'test':
        names = [row.name for row in Javalog.objects.all()]
    names = sorted(list(set(names)))
    name = request.GET.get('name',)
    idc = request.GET.get('idc',)
    return render_to_response('downwar.html',locals())
@login_required
def hosts(request):
    user = request.user
    #idcs = [row.idc for row in Javalog.objects.filter(username=user)]
    #idcs = sorted(list(set(idcs)))
    idcs = ['B28','PRE','TJ','ceshi']
    return render_to_response('hosts.html',locals())
def showhosts(request):
    user = request.user
    idc = request.GET.get('idc',)
    passwd = onlinepasswd
    cmd = "cat /opt/jiuxian/common/host_tab/%s.hosts" % idc
    if idc == "ceshi":
        ret = os.popen("cat /opt/jiuxian-test/common/host_tab/ceshi.hosts").read()
    else:
        ret = ssh("192.168.10.249",passwd,cmd)["192.168.10.249"]
    json = simplejson.dumps(ret)
    return HttpResponse(json)
def hostedit(request):
    user = request.user
    idc = request.POST.get('idc')
    data = request.POST.get('data')
    if idc == 'ceshi':
        cmd = 'echo "%s" |sudo tee /opt/jiuxian-test/common/host_tab/ceshi.hosts &&echo edit ok' % data
        passwd = testpasswd
        ret = ssh("192.168.6.30",passwd,cmd)["192.168.6.30"].split('\n')
    else:
        passwd = onlinepasswd
        cmd = 'echo "%s" |sudo tee /opt/jiuxian/common/host_tab/%s.hosts &&echo edit ok' % (data,idc)
        ret = ssh("192.168.10.249",passwd,cmd)["192.168.10.249"].split('\n')
    if 'edit ok' in ret:
        ret = "修改成功！"
    #json = simplejson.dumps(ret)
    return HttpResponse(ret)
def hostsync(request):
    user = request.user
    idc = request.POST.get('idc')
    if str(user) == 'root' or str(user) == 'test':
        if idc == "ceshi":
            ret = os.popen("sh /opt/jiuxian-test/update/jiuxian_ip_ceshi_update.sh uphosts www ceshi").read()
    else:
        ret = ""
    json = simplejson.dumps(ret)
    return HttpResponse(ret)

@login_required
def cdn(request):
    user = request.user  
    ltime = request.GET.get('ltime')      
    return render_to_response('cdnlog.html',locals())
def chart(request):
    user = request.user
    site = request.GET.get('site')
    cdn = request.GET.get('cdn')
    ltime = request.GET.get('ltime')
    Cdnlog.objects.filter(name=site,cdn=cdn,ltime=ltime)
    pvs = [row.pv for row in Cdnlog.objects.filter(name=site,cdn=cdn,ltime=ltime)]
    sizes = [row.size for row in Cdnlog.objects.filter(name=site,cdn=cdn,ltime=ltime)]
    hit = Cdnlog.objects.filter(name=site,cdn=cdn)[0].hit
    ret = []
    #f = os.popen("tail -n %s /data/javalog/javalog/cdnlog" % ltime).readlines()
    for i in f:
        L = i.strip().split()
        #d = {"name":L[0],"value":L[1],"color":'#a5c2d5'}
        d = {"name":"手机","value":L[1],"color":'#a5c2d5'}
        ret.append(d)
    ret = "%s" % ret
    #json = simplejson.dumps(ret,ensure_ascii=True)
    #ret = '[{"name":"手机","value":20,"color":"#a5c2d5"},{"name":"电脑","value":30,"color":"#a5c2d5"}]'
    return HttpResponse(ret)    
    
@login_required
def dblog(request):
    user = request.user
    dbname = request.GET.get('dbname')
    ip = request.GET.get('ip')
    num = request.GET.get('num')
    dbnames = [row.dbname for row in Dblog.objects.all()]
    dbnames = sorted(list(set(dbnames)))
    if not num:
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
    #passwd = onlinepasswd
    passwd = 'jiuxian2014'
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
    #passwd = onlinepasswd
    passwd = 'jiuxian2014'
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
    #passwd = onlinepasswd
    passwd = 'jiuxian2014'
    f = '/my/log/%s' % file
    sizecmd = 'du -sm %s' % f
    logsize = int(ssh(ip,passwd,sizecmd)[ip].split()[0])
    if logsize < 20:
        file = rnum + "_" + file
        t = paramiko.Transport((ip,9830))
        t.connect(username='jiuxian',password=passwd)
        sftp=paramiko.SFTPClient.from_transport(t)
        sftp.get(f,'/data/javalog/javalog/static/down/%s' % file)
        json = simplejson.dumps('ok')
    else:
        json = simplejson.dumps('false')
    return HttpResponse(json)
