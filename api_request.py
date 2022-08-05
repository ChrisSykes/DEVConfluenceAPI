# #DOC: https://atlassian-python-api.readthedocs.io/confluence.html 
# from atlassian import Confluence
# import json

# class Conflu: 
#     def __init__(self, wikiurl, wikiusername, wikipassword):
#         confluence = Confluence(
#             url=wikiurl,
#             username=wikiusername,
#             password=wikipassword)
#         self.confluence = confluence


# wikiurl = 'http://localhost:8090'
# wikiusername = 'admin'
# wikipassword = 'admin'
# conflu = Confluence(wikiurl, wikiusername, wikipassword)


# space = "TES"
# title = "test"
# body = "Edit v3" 


# spaceContent = conflu.update_page(conflu.get_page_id(space, title), title, body, parent_id=None, type='page', representation='storage', minor_edit=False)

#DOC: https://atlassian-python-api.readthedocs.io/confluence.html 
import requests
from requests.auth import HTTPBasicAuth
from atlassian import Confluence
import json

confluence = Confluence(
    url='http://localhost:8090',
    username='admin',
    password='admin')

wikiurl = 'http://localhost:8090'
username = 'admin'
password = 'admin'
basic = HTTPBasicAuth(username, password)


spaceID = "TES"
contentID = '1572865'
titleID = 'json'
bodyID = "Edit v2" 


status = requests.get(wikiurl + '/rest/viewtracker/1.0/report/contents/' + contentID + '/visits', auth=basic)
jsonStatus = status.text
dumpsStatus = json.loads(jsonStatus)

userIdPrint = dumpsStatus['results'][0]['user']['username']
viewNumberPrint = dumpsStatus['results'][0]['views']

print(userIdPrint, viewNumberPrint)

print(confluence.get_page_id(spaceID, titleID))

bodyID = f'''<p class="auto-cursor-target">
  <br/>
</p>
<table class="wrapped">
  <colgroup>
    <col/>
    <col/>
  </colgroup>
  <tbody>
    <tr>
      <th scope="col">userid</th>
      <th scope="col">views</th>
    </tr>
    <tr>
      <td>{userIdPrint}</td>
      <td>{viewNumberPrint}</td>
    </tr>
  </tbody>
</table>
<p class="auto-cursor-target">
  <br/>
</p>
''' 

spaceContent = confluence.update_page(contentID, titleID, bodyID)

