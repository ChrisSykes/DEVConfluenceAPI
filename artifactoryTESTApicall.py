#https://artifactory.itcm.oneadr.net/api/storageinfo


import requests
from requests.auth import HTTPBasicAuth
import json

url = 'https://artifactory.itcm.oneadr.net/api/storageinfo'
username = 'm013791'
password = 'Paszte20'
basic = HTTPBasicAuth(username, password)

status = requests.get(url, auth=basic)

print(status.text)

print(status['packageType'])
