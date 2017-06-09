#!/usr/bin/python
# -*- coding: utf-8 -*-
import itchat
import paramiko
import os
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

hostname = ''
username = ''
port = 
key_file = '/Users/wenjun/.ssh/id_rsa'
filename = '/Users/wenjun/.ssh/known_hosts'

#查看主机状态

def sshPingPc(hostname,username,port,key_file,filename):
		paramiko.util.log_to_file('ssh_key-login.log')
		privatekey = os.path.expanduser(key_file) 
		try:
		    key = paramiko.RSAKey.from_private_key_file(privatekey)
		except paramiko.PasswordRequiredException:
		    key = paramiko.RSAKey.from_private_key_file(privatekey,key_file_pwd)
		 
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys(filename=filename)
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=hostname,username=username,pkey=key,port=port)
		stdin,stdout,stderr=ssh.exec_command('ping 192.168.1.182 -c 5 | grep 64 | cut -d " " -f 1|tail -n 1')
		sshCheckOpen = stdout.read()
		commandReturn =sshCheckOpen.strip('\n')
		ssh.close()
		if commandReturn == '64':
			return 1
		else:
			return 0
#唤醒方法
def  WakeOnLanPc(hostname,username,port,key_file,filename):
		paramiko.util.log_to_file('ssh_key-login.log')
		privatekey = os.path.expanduser(key_file) 
		try:
		    key = paramiko.RSAKey.from_private_key_file(privatekey)
		except paramiko.PasswordRequiredException:
		    key = paramiko.RSAKey.from_private_key_file(privatekey,key_file_pwd)
		 
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys(filename=filename)
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=hostname,username=username,pkey=key,port=port)

		stdin,stdout,stderr=ssh.exec_command('wakeonlan -i 192.168.1.0 14:dd:a9:ea:0b:96')
		sshCheckOpen = stdout.read()
		commandReturn =sshCheckOpen.strip('\n')
		ssh.close()
		return 0

#创建文件
def mkdirfile():

	if os.path.exists('/www/shutdown'):
		print '文件已存在'
	else:
		os.system('touch /www/shutdown')
		createfile = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		print createfile+' 执行开机消息成功'
	return 0

#开机方法
def openPC():

	checkPcStatus = sshPingPc(hostname,username,port,key_file,filename)
	#进行判断，如果为64，则说明 ping 成功，说明设备已经在开机状态，程序结束，否则执行唤醒
	if checkPcStatus == 1:
		connect_ok_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		itchat.send(connect_ok_time+u' 设备已经开机', toUserName='filehelper')
	else:
		#设备未开机，执行唤醒命令
		ssh_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		itchat.send(ssh_time+u' 开始连接远程主机', toUserName='filehelper')
		#唤醒
		WakeOnLanPc(hostname,username,port,key_file,filename)
		wakeonlan_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		itchat.send(wakeonlan_time+u' 执行唤醒，等待设备开机联网', toUserName='filehelper')
		#由于开机需要一些时间去启动网络，所以这里等等20s	
		time.sleep(60)
		checkPcStatus = sshPingPc(hostname,username,port,key_file,filename)
		if checkPcStatus == 1:
			connect_ok_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
			itchat.send(connect_ok_time+u' 设备唤醒成功，您可以远程连接了', toUserName='filehelper')
		else:
			connect_err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			itchat.send(connect_err_time+u' 设备唤醒失败，请检查设备是否连接电源', toUserName='filehelper')
				
#关机方法

def shutdownPc():
	if os.path.exists('/www/shutdown'):
		#删除shutdown 文件
		rmfile = os.system('rm -rf /www/shutdown')
		if rmfile == 0:
			shutdowninfo = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
			print shutdowninfo+' 执行关机消息成功'
		shutdown_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
		itchat.send(shutdown_time+u' 正在关机....', toUserName='filehelper')		
		#等等60秒后确认，因为关机需要一段时间，如果设置太短，可能网络还没断开
		time.sleep(60)
		checkPcStatus = sshPingPc(hostname,username,port,key_file,filename)
		if checkPcStatus == 0:
			shutdown_success_err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			itchat.send(shutdown_success_err_time+u' 关机成功', toUserName='filehelper')
		else:
			shutdown_err_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
			itchat.send(shutdown_err_time+u' 关机失败，请连接桌面检查客户端程序是否正常执行', toUserName='filehelper')
	else:
			getinfotime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
			itchat.send(getinfotime+u' 提示：您的设备未开机', toUserName='filehelper')


#微信登陆
@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
	if msg['ToUserName'] != 'filehelper': return
	if msg['Text'] ==  u'开机':
		mkdirfile()
		openPC()
	if msg['Text'] ==  u'关机':
		shutdownPc()


itchat.auto_login(hotReload=True,enableCmdQR=2)
itchat.run()
