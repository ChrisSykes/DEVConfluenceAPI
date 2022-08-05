pip list
python --version
python3 --version

echo "###########################"

#pip install virtualenv -i https://artifactory.itcm.oneadr.net/api/pypi/pypi-remote/simple/
mkdir ${bamboo.agentWorkingDirectory}/conflu
/usr/bin/python3 -m venv ${bamboo.agentWorkingDirectory}/conflu
virtualenv -p python3 ${bamboo.agentWorkingDirectory}/conflu
source ${bamboo.agentWorkingDirectory}/conflu/bin/activate

#python3 -m pip install --upgrade pip -i https://artifactory.itcm.oneadr.net/api/pypi/pypi-remote/simple/
python3 -m pip install atlassian-python-api -i https://artifactory.itcm.oneadr.net/api/pypi/pypi-remote/simple/
python3 -m pip install requests -i https://artifactory.itcm.oneadr.net/api/pypi/pypi-remote/simple/
#python3 -m pip install json -i https://artifactory.itcm.oneadr.net/api/pypi/pypi-remote/simple/
echo "###########################"

pip list

python3 <<EOF
import getpass
import json
import requests
from requests.auth import HTTPBasicAuth
from atlassian import Confluence

class Artifactory:
    def listRepositories(url, user, password):
        try:
            api = '/api/repositories'
            link = url + api
            print("Check API URL:", link)
            response = requests.get(link, auth=HTTPBasicAuth(user, password))
            return (response.text)
        except Exception as exp:
            print(exp)

    def listRepositoriesByPackageType(packageType, data):
        try:
            repoList = []
            for i in data:
                if i['packageType'] == packageType:
                    repoList.append(i)
            return repoList
        except Exception as exp:
            print(exp)
            
    def checkStorage(url, user, password):
        try:
            api = "/api/storageinfo"
            link = url + api
            print("Check API URL:", link)
            response = requests.get(link, auth=HTTPBasicAuth(user, password))
            return (response.text)
        except Exception as exp:
            print(exp)

class Conflu:
    def __init__(self, wikiUrl, wikiUsername, wikiPassword):
        confluence = Confluence(
            url=wikiUrl,
            username=wikiUsername,
            password=wikiPassword)
        self.confluence = confluence

    def getWikiPageId(self, wikiSpace, wikiTitle):
        try:
            wikiPageId = self.confluence.get_page_id(wikiSpace, wikiTitle)
            return wikiPageId
        except Exception as exp:
            print(exp)

    def updateWikiPage(self, data, wikiPageId, wikiTitle):
        self.confluence.update_page(page_id=wikiPageId, title=wikiTitle, body=data, parent_id=None, type='page',
                               representation='storage', minor_edit=False)

    def generateContentForRepositories(self, data):
        body = '<table><colgroup><col/><col/><col/><col/><col/></colgroup><tbody><tr><th>RepositoryName</th><th>RepositoryType</th><th>RepositoryPackage</th><th>RepositoryUrl</th><th>Owner</th></tr>'
        for item in data:
            if 'description' in item:
                body = body + '<tr><td>' + item['key'] + '</td><td>' + item['type'] + '</td><td>' + item[
                    'packageType'] + '</td><td>' + item['url'] + '</td><td>' + item['description'] + '</td></tr>'
            else:
                body = body + '<tr><td>' + item['key'] + '</td><td>' + item['type'] + '</td><td>' + item[
                    'packageType'] + '</td><td>' + item['url'] + '</td><td></td></tr>'
        body = body + '</tbody></table>'
        return body

    def generateContentForDockerRegistry(self, data):
        body = '<table><colgroup><col/><col/><col/><col/><col/></colgroup><tbody><tr><th>RepositoryName</th><th>RepositoryType</th><th>RepositoryPackage</th><th>Docker Alias</th><th>Owner</th></tr>'
        for item in data:
            item['url'] = item['key'] + '.docker.itcm.oneadr.net'
            if 'description' in item:
                body = body + '<tr><td>' + item['key'] + '</td><td>' + item['type'] + '</td><td>' + item[
                    'packageType'] + '</td><td>' + item['url'] + '</td><td>' + item['description'] + '</td></tr>'
            else:
                body = body + '<tr><td>' + item['key'] + '</td><td>' + item['type'] + '</td><td>' + item[
                    'packageType'] + '</td><td>' + item['url'] + '</td><td></td></tr>'
        body = body + '</tbody></table>'
        return body
        
    def generateContentForStorageInfo(self, data):
        body = '<table><colgroup><col/><col/><col/><col/><col/><col/><col/></colgroup><tbody><tr><th>RepositoryName</th><th>RepositoryType</th><th>RepositoryPackage</th><th>used space</th><th>files count</th><th>folders count</th><th>percentage</th></tr>'
        for item in data["repositoriesSummaryList"]:
            if item["repoType"] == 'CACHE':
                item["repoType"] = 'REMOTE'
            if 'packageType' in str(item):
                #print(item)
                body = body + '<tr><td>' + item['repoKey']   + '</td><td>' + item['repoType'] + '</td><td>' + item['packageType'] + '</td><td>' + str(item['usedSpace']) + '</td><td>' + str(item['filesCount']) + '</td><td>' + str(item['foldersCount']) + '</td><td>' + str(item['percentage']) + '</td></tr>'
                #body = body + '<tr><td>' + str(item['repoKey'])   + '</td><td>' + str(item['repoType']) + '</td><td>' + str(item['packageType']) + '</td><td>' + str(item['usedSpace']) + '</td><td>' + str(item['filesCount']) + '</td><td>' + str(item['foldersCount']) + '</td></tr>'
        body = body + '</tbody></table>'
        return body


### get list of repositories from Artifactory ###
artifactoryUrl = 'https://artifactory.itcm.oneadr.net'
artifactoryUser = '${bamboo.artifactoryUser}'
artifactoryPassword = '${bamboo.artifactoryPassword}'
tempBody = Artifactory.listRepositories(artifactoryUrl, artifactoryUser, artifactoryPassword)
artifactoryRepostotires = json.loads(tempBody)

# Confluence section
wikiUrl = 'https://wiki.itgit.oneadr.net'
wikiUsername = '${bamboo.wikiUser}'
wikiPassword = '${bamboo.wikiPassword}'

wikiSpace = "SREToolsDoc"
conn = Conflu(wikiUrl, wikiUsername, wikiPassword)


### update wiki page repository ###
wikiTitle = "Repositories"
pageId = ""
try:
    pageId = conn.getWikiPageId(wikiSpace, wikiTitle)
    print('Confluence '+ wikiSpace, wikiTitle + ': ' + pageId)

    wikiBody = conn.generateContentForRepositories(artifactoryRepostotires)
    #print(wikiBody)
    conn.updateWikiPage(wikiBody, pageId, wikiTitle)
except Exception as exp:
    print(exp)

### update wiki page for docker registry ###
wikiTitle = "Docker Repositories - aliases"
pageId = ""

try:
    pageId = conn.getWikiPageId(wikiSpace,wikiTitle)
    print('Confluence '+ wikiSpace, wikiTitle + ': ' + pageId)

    lista = Artifactory.listRepositoriesByPackageType("Docker", artifactoryRepostotires)
    wikiBody = conn.generateContentForDockerRegistry(lista)
    #print(wikiBody)
    conn.updateWikiPage(wikiBody, pageId, wikiTitle)
except Exception as exp:
    print(exp)
    
### update wiki page about storage info ###
wikiSpace = "SRETechDoc"
wikiTitle = "StorageInfo"
pageId = ""

try:
    pageId = conn.getWikiPageId(wikiSpace, wikiTitle)
    print('Confluence '+ wikiSpace, wikiTitle + ': ' + pageId)
    lista = Artifactory.checkStorage(artifactoryUrl, artifactoryUser, artifactoryPassword)
    lista = json.loads(lista)

    wikiBody = conn.generateContentForStorageInfo(lista)
    #print(wikiBody)
    conn.updateWikiPage(wikiBody, pageId, wikiTitle)
except Exception as exp:
    print(exp)
EOF
