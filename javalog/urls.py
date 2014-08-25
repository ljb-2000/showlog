from django.conf.urls import patterns, include, url

from django.contrib import admin
from javalog.views import *
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', index, name='index'),
    url(r'^login/$', login ,name='login'),
    url(r'^logout/$', logout ,name='logout'),
    url(r'^account_login/$', account_login ,name='account_login'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^javalog/$', javalog,name='javalog'),
    url(r'^getIdc$', getIdc,name='getIdc'),
    url(r'^getIp$', getIp,name='getIp'),
    url(r'^getFile$', getFile,name='getFile'),
    url(r'^showLog$', showLog,name='showLog'),
    url(r'^restart$', restart,name='restart'),
    url(r'^stop$', stop,name='stop'),
    url(r'^status$', status,name='status'),
    url(r'^down$', down,name='down'),
    url(r'^redis/$', redis,name='redis'),
    url(r'^redisgetip$', redisgetip,name='redisgetip'),
    url(r'^redisgetfile$', redisgetfile,name='redisgetfile'),
    url(r'^redisview$', redisview,name='redisview'),
    url(r'^redisedit$', redisedit,name='redisedit'),
    url(r'^redisstatus$', redisstatus,name='redisstatus'),
    url(r'^redisrestart$', redisrestart,name='redisrestart'),
    url(r'^zookeeper/$', zookeeper,name='zookeeper'),
    url(r'^zookeepergetip$', zookeepergetip,name='zookeepergetip'),
    url(r'^zookeepergetfile$', zookeepergetfile,name='zookeepergetfile'),
    url(r'^zookeeperview$', zookeeperview,name='zookeeperview'),
    url(r'^zookeeperedit$', zookeeperedit,name='zookeeperedit'),
    url(r'^zookeeperstatus$', zookeeperstatus,name='zookeeperstatus'),
    url(r'^zookeeperrestart$', zookeeperrestart,name='zookeeperrestart'),
    url(r'^downwar$', downwar,name='downwar'),
    url(r'^war$', war,name='war'),
    url(r'^hosts$', hosts,name='hosts'),
    url(r'^showhosts$', showhosts,name='showhosts'),
    url(r'^hostedit$', hostedit,name='hostedit'),
    url(r'^hostsync$', hostsync,name='hostsync'),
    url(r'^cdn$', cdn,name='cdn'),
    url(r'^chart$', chart,name='chart'),
    url(r'^dblog$', dblog,name='dblog'),
    url(r'^getDbip$', getDbip,name='getDbip'),
    url(r'^showDblog$', showDblog,name='showDblog'),
    url(r'^getDbfile$', getDbfile,name='getDbfile'),
    url(r'^downDblog$', downDblog,name='downDblog'),
)
urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT )
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT )
