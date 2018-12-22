#encoding:utf8
headers = {}
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30"
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
headers["Accept-Language"] = "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
headers["Accept-Encoding"] = "gzip, deflate"
headers["Upgrade-Insecure-Requests"] = "1"

daily_url = 'https://cassandra.cerias.purdue.edu/CVE_changes/today.html'

mysql_host = '127.0.0.1'
mysql_username = 'root'
mysql_password = ''
mysql_db = 'crawlcve'

mail_sender = '541794749@qq.com'
mail_receivers = ['']    # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

# 第三方 SMTP 服务
mail_config = {}
mail_config['mail_host'] = "smtp.qq.com"  #设置服务器
mail_config['mail_user'] = "541794749@qq.com"    #用户名
mail_config['mail_pass'] = ""   #口令 