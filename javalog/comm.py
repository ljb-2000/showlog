base_dir = '/data/javalog/'
def ssh(ip,passwd,cmd):
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip,9830,'jiuxian',passwd,timeout=10)
    except:
        return {ip:"Error: connect fail !!!"}
    try:
        stdin, stdout, stderr = ssh.exec_command("export LANG=en_US.UTF-8 ; %s" % cmd)
    except:
        return {ip:"Error: exec fail !!!"}
    i = stderr.readlines()
    if i:
        return {ip:''.join(i)}
    return {ip:''.join(stdout.readlines())}
    ssh.close()
