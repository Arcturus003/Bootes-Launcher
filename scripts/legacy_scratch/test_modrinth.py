import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://api.modrinth.com/v2/search?query=Tensura'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode())
        for h in data['hits']:
            print(h['title'], h['project_id'])
except Exception as e:
    print(e)
