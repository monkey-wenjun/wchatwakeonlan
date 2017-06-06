 #!/bin/env python
# -*- coding: UTF-8 -*-
import itchat
import paramiko
import os
import time

#主机地址
hostname = ''
#用户名
username = ''
#端口
port =  
#ssh 密钥位置
key_file = '/Users/wenjun/.ssh/id_rsa' 

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
	#如果消息内容为开机，则执行 ssh 连接
    if msg['Text'] ==  u'开机':
		paramiko.util.log_to_file('ssh_key-login.log')
		privatekey = os.path.expanduser(key_file) 
		try:
		    key = paramiko.RSAKey.from_private_key_file(privatekey)
		except paramiko.PasswordRequiredException:
		    key = paramiko.RSAKey.from_private_key_file(privatekey,key_file_pwd)
		 
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys(filename='/Users/wenjun/.ssh/known_hosts')
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=hostname,username=username,pkey=key,port=port)
		#执行唤醒命令
		stdin,stdout,stderr=ssh.exec_command('wakeonlan -i 192.168.1.0 14:dd:a9:ea:0b:96')
		print stdout.read()
		#由于开机需要一些时间去启动网络，所以这里等等60s
		time.sleep(60)
		#执行 ping 命令，-c 1 表示只 ping 一下，然后过滤有没有64，如果有则获取64并转换为 int 类型传给sshConStatus
		stdin,stdout,stderr=ssh.exec_command('ping 192.168.1.182 -c 1 | grep 64 | cut -b 1,2')
		sshConStatus = int(stdout.read())
		# print type(sshComStatus)
		#进行判断，如果为64，则说明 ping 成功，设备已经联网，可以进行远程连接了，否则发送失败消息
		if sshConStatus == 64:
			msg['Text'] = u'设备唤醒成功，您可以远程连接了'
			return msg['Text']
		else:
			print sshComStatus
			msg['Text'] = u'设备唤醒失败，请检查设备是否连接电源'
			return msg['Text']
		ssh.close()
itchat.auto_login(hotReload=True,enableCmdQR=2)
itchat.run()