import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://api.modrinth.com/v2/project/roJlZcNx/version'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Antigravity/1.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        versions = json.loads(response.read().decode())
        for v in versions:
            if 'fabric' in v['loaders'] and '1.21.1' in v['game_versions']:
                print(v['files'][0]['url'])
                break
except Exception as e:
    print(e)
