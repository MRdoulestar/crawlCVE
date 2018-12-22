#encoding:utf8

import os
import sys
parentdir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#把目录加入环境变量
sys.path.insert(0,parentdir)

import pymysql
import config
import requests
import json
from zipfile import ZipFile


def download_json():
    # Create the folder
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    # Download json file
    for year in range(2002, 2019):
        filename = 'nvdcve-1.0-' + str(year) + '.json.zip'
        url = 'https://nvd.nist.gov/feeds/json/cve/1.0/' + filename
        if os.path.exists('downloads/nvdcve-1.0-' + str(year) + '.json.zip'):
            print('Exist file: ' + filename + ' Pass downloading...')
            if not os.path.exists('downloads/nvdcve-1.0-' + str(year) + '.json'):
                # Extract ZIP
                unzip('downloads/' + filename, 'downloads/')
            continue
        print('Downloading ' + filename + '...')
        res = requests.get(url)
        with open('downloads/' + filename, 'wb') as f:
            f.write(res.content)
        print('Done')
        # Extract ZIP
        unzip('downloads/' + filename, 'downloads/')


def unzip(fileName, path):
    print "Extracting: " + fileName,
    zip = ZipFile(fileName)
    zip.extractall(path)
    zip.close()
    print " [DONE]"


def unserialize(path):
    data = []
    for year in range(2002, 2019):
        filename = path + 'nvdcve-1.0-' + str(year) + '.json'
        print('Unserialize' + filename + '...')
        with open(filename, 'r') as f:
            cve_json = json.load(f)['CVE_Items']

        length = len(cve_json)
        print('Number: ' + str(length))

        for j in range(0, length):
            temp = {}
            # print(cve_json[0]['cve'])
            temp['CVE_ID'] = cve_json[j]['cve']['CVE_data_meta']['ID']
            temp['Description'] = cve_json[j]['cve']['description']['description_data'][0]['value']
            temp['Assigning_CNA'] = ''
            temp['Data_Entry_Created'] = cve_json[j]['publishedDate']

            refer = ''
            arr = cve_json[j]['cve']['references']['reference_data']
            for i in arr:
                refer += i['url'] + ','
            temp['Reference_url'] = refer
            
            print('Unserializing ' + temp['CVE_ID'])
            data.append(temp)
        print('Done')
    return data


# Store the CVE details into MySql
def store_cve(cve_infos):
    print('Storing the CVEs info...')
    conn = pymysql.connect(host=config.mysql_host, port=3306, 
        user=config.mysql_username, passwd=config.mysql_password, db=config.mysql_db)
    cursor = conn.cursor()

    for dic in cve_infos:
        print('Storing: ' + dic['CVE_ID']) 
    	# Format the args
        # args = (dic["CVE_ID"],dic["Description"],dic["Assigning_CNA"],dic["Data_Entry_Created"],dic["Reference_url"])
        sql = '''INSERT INTO data(cve_id,description,cna,entry_created,ref_url) VALUES ("%s","%s","%s","%s","%s")''' % (dic["CVE_ID"],dic["Description"],dic["Assigning_CNA"],dic["Data_Entry_Created"],dic["Reference_url"])
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            conn.rollback()
    conn.close()
    print('Down')


# Download CVE JSON Data
download_json()
# Loads JSON
data = unserialize('downloads/')
# Store CVEs in MySql
store_cve(data)


