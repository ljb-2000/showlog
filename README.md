JX日志查看平台 
-
###日志查看平台功能说明 
1、tomcat启动日志、java程序日志实时查看和下载，tomcat重启、停止和查看状态 <br>
2、redis配置文件查看和编辑，redis重启和查看状态 <br>
3、zookeeper配置文件查看和编辑，zookeeper重启和查看状态 <br>
4、war包和公共jar包下载 <br>
5、服务器hosts文件查看、编辑和推送 <br>
6、数据库错误日志查看和下载 <br>
7、文件共享库，文件文件上传、编辑、删除和下载 <br>
8、cdn日志分析系统，按域名和时间段选择图表形式展示cdn日志分析报告，能指定日志查看详细报告。 <br>

###日志查看平台
mv /data/javalog/db.sqlite3.demo  /data/javalog/db.sqlite3<br>
mkdir -p /data/download/files<br>
/data/javalog/manage.py runserver 0.0.0.0:8001  #启动主程序<br>
cd /data/download/;nohup python -m SimpleHTTPServer 8008 & #启动日志下载web服务<br>
IE访问http://ip:8001<br>
用户名：root<br>
密码：123456<br>
注意：使用过程根据实际环境修改ip地址，ssh端口号，ssh登录账户密码等，需改动的地方可能比较多<br>
