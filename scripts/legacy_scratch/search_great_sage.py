import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search():
    query = urllib.parse.quote('Great Sage Tensura')
    url = f'https://api.modrinth.com/v2/search?query={query}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Antigravity/1.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            for hit in data['hits']:
                print(hit['title'] + " - " + hit['project_id'])
    except Exception as e:
        print(e)

search()
