akamai CCU 和 ECCU 的API用法      
===========================
介绍如何使用akamai API进行刷新文件和目录:
---
1.CCU刷新
---
### 1.必须使用python2.7.5或以上的环境
### 2.下载代码放到服务器的任意目录
###
		cd /examples/python/tools/ && python setup.py install
### 3.生成.edgerc文件
###	
		首先去akamai控制台 配置-->管理API-->创建凭据并下载
		比如我生成的凭据文件叫做test.txt
###
		执行python /examples/python/gen_edgerc.py test.txt
###
		执行完成后会在root目录下生成.edgrc文件
### 4.验证文件是否生效
###
		然后执行python /examples/python/verify_creds.py 来验证生成证书拼接是否正确

### 5.执行刷新命令，即可刷新文件
###
		python /examples/python/akamai_publish_file.py 加域名及文件路径
		如：我的文件为www.test.com/a/b/c/d.txt
		python /examples/python/akamai_publish_file.py http://www.test.com/a/b/c/d.txt
		执行5-10秒后即可刷新完成。

ECCU 刷新
---
###1.环境准备
		1.必须使用python2.7.5或以上的环境
		2.pip install suds
		3.pip install requests
###2.修改配置文件（settings.py-->username and password and notification_email）
		
		import os
		username='input your username'
		password='input your password'
		notification_email='input your notification email'
		endpoint='https://control.akamai.com/webservices/services/PublishECCU'
		wsdl_url='file://%s' % os.path.join(os.path.dirname(__file__), 'PublishECCU.wsdl')
		
		print wsdl_url
		try:
		    from settings_local import *
		except ImportError:
    		pass
###3.执行刷新命令

###
		比如刷新http://www.test.com/a/b/这个目录执行以下命令：
		python /examples/python/akamai_publish_dir.py http://www.test.com/a/b/
		执行完成后会显示生成的刷新ID，最多30-40分钟即可刷新完成。完后后会有邮件告知。
###


		


 


