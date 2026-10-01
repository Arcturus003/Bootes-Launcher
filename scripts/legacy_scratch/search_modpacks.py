import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search(query):
    encoded = urllib.parse.quote(query)
    url = f'https://api.modrinth.com/v2/search?query={encoded}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Antigravity/1.0'})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            if data['hits']:
                hit = data['hits'][0]
                print(hit['title'] + " - https://modrinth.com/modpack/" + hit['slug'])
    except Exception as e:
        print(e)

search('TenSura (That Time I Got Reincarnated as a Slime)')
search('Tensura Neo Otherworld')
