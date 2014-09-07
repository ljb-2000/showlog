
###日志查看平台
mv /data/javalog/db.sqlite3.demo  /data/javalog/db.sqlite3<br>
mkdir -p /data/download/files<br>
/data/javalog/manage.py runserver 0.0.0.0:8001<br>  #启动主程序
cd /data/download/;nohup python -m SimpleHTTPServer 8008 & #启动日志下载web服务
IE访问http://ip:8001<br>
用户名：root<br>
密码：123456<br>
注意：使用过程根据实际环境修改ip地址，ssh端口号，ssh登录账户密码等，需改动的地方可能比较多<br>
