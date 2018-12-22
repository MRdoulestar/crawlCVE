#encoding:utf8

import requests
import re
import pymysql
from bs4 import BeautifulSoup
import config
import function.mail as mail
import time

# Get the CVEs' url
def init_urls():
    urls = []
    res = requests.get(config.daily_url)
    # print res.text
    date = re.search(r'<BR>(.*)<BR>', res.text)
    if date:
        date = date.group(1)
    u = re.search(r'<HTML><BODY>(.*)Graduations', res.text, re.S)
    if u:
        CVEList_html = u.group(1)

    soup = BeautifulSoup(CVEList_html, 'html.parser')
    for a in soup.find_all('a'):
        uri = a["href"]
        urls.append(uri)
        # print(a['href'])
        # print(a.string)
    return urls

# Download CVE details from URLs
def download_cve_info(urls):
    cve_infos = []
    for url in urls:
        temp = {}
        print("Handling with: " + url)
        res = requests.get(url, headers = config.headers, timeout=60)
        # Deal with the slow network
        while res.status_code != 200:
            print("Retrying..." + url)
            res = requests.get(url, headers = config.headers, timeout=60)
        soup = BeautifulSoup(res.text, "html.parser")
        # Get the CVE id
        CVE_ID = str(soup.find(nowrap="nowrap").find("h2").string)
        print CVE_ID
        table = soup.find(id = "GeneratedTable").find("table")
        Description = table.find_all("tr")[3].find("td").string
        # Get the Description
        Assigning_CNA = table.find_all("tr")[8].find("td").string
        # Get the Assigning_CNA
        Data_Entry_Created = table.find_all("tr")[10].find("b").string
        # Get the reference 
        s = re.search(r'References(.*)Assigning CNA', res.text, re.S)
        if s:
            ss = s.group(1)
        urls=re.findall(r"<a.*?href=.*?<\/a>",ss,re.I)
        Reference = []
        for i in urls[1:]:
            Reference.append(i.split(">")[1].split("<")[0])
        Reference_url = ",".join(Reference)

        temp['CVE_ID'] = CVE_ID
        temp['Description'] = Description
        temp['Assigning_CNA'] = Assigning_CNA
        temp['Data_Entry_Created'] = Data_Entry_Created
        temp['Reference_url'] = Reference_url
        cve_infos.append(temp)
    return cve_infos

# Store the CVE details into MySql
def store_cve(cve_infos):
    conn = pymysql.connect(host=config.mysql_host, port=3306, 
        user=config.mysql_username, passwd=config.mysql_password, db=config.mysql_db)
    cursor = conn.cursor()

    for dic in cve_infos:
    	# Format the args
        # args = (dic["CVE_ID"],dic["Description"],dic["Assigning_CNA"],dic["Data_Entry_Created"],dic["Reference_url"])
        sql = '''INSERT INTO data(cve_id,description,cna,entry_created,ref_url) VALUES ("%s","%s","%s","%s","%s")''' % (dic["CVE_ID"],dic["Description"],dic["Assigning_CNA"],dic["Data_Entry_Created"],dic["Reference_url"])
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            conn.rollback()
    conn.close()

# Send mail
def send_cve_mail(cve_infos):
    # Generate mail_contents
    mail_msg = """<h4>每日CVE推送...</h4><table><thead><tr><th>CVEID</th><th>描述</th><th>CNA</th><th>CVE创建时间</th><th>参考</th></tr></thead><tbody>"""
    # mail_msg = """<h4>每日CVE推送...</h4><table><thead><tr><th>CVEID</th><th></th></thead><tbody>"""
    for dic in cve_infos:
        mail_msg += '''<tr>%s</tr><tr>%s</tr><tr>%s</tr><tr>%s</tr><tr>%s</tr><br>\n''' % (dic["CVE_ID"].encode('utf-8'),dic["Description"].encode('utf-8'),dic["Assigning_CNA"].encode('utf-8'),dic["Data_Entry_Created"].encode('utf-8'),dic["Reference_url"].encode('utf-8'))
        # mail_msg += '''<tr>%s</tr><tr><a href="%s"></tr>''' % (dic["CVE_ID"].encode('utf-8'), 'http://cve.mitre.org/cgi-bin/cvename.cgi?name=' + dic["CVE_ID"].encode('utf-8'))
    mail_msg += "</tbody></table>"
    # Send mail
    for receiver in config.mail_receivers:
        print('Sending ' + receiver)
        print(mail_msg)
        mail.sendmail(config.mail_sender, receiver, mail_msg, config.mail_config)


urls = []
cve_infos = []
# Get the CVE urls
print("Handling CVEs' URL...")
urls = init_urls()
print("Down")
# Get the details of CVEs
print("Geting the details of CVEs...")
cve_infos = download_cve_info(urls)
print("Down")
# Store the CVEs' info
print("Storing the CVEs' info...")
# store_cve(cve_infos)
print("Down")
# Send mail
print("Sending the mail...")
send_cve_mail(cve_infos)
print("Down")