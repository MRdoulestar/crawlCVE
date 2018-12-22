#coding:utf8
 
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
 

def sendmail(sender, receiver, mail_msg, mail_config):
    # mail_msg = """
    # <p>每日CVE推送...</p>
    # <p><a href="http://www.runoob.com">链接</a></p>
    # """
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = Header(sender, 'utf-8')
    message['To'] =  Header(receiver, 'utf-8')
    
    subject = '每日CVE更新推送-' + str(time.localtime()[0]) + '.' + str(time.localtime()[1]) + '.' + str(time.localtime()[2])
    message['Subject'] = Header(subject, 'utf-8')   
    
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_config['mail_host'], 25)    # 25 为 SMTP 端口号
        smtpObj.login(mail_config['mail_user'],mail_config['mail_pass'])  
        smtpObj.sendmail(sender, receiver, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException,e:
        print e
        print "Error: 无法发送邮件"
