import urllib.request
import json
import urllib.parse

def search_versions():
    url = 'https://api.modrinth.com/v2/project/tensura/version'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Antigravity/1.0'})
        with urllib.request.urlopen(req) as response:
            versions = json.loads(response.read().decode())
            for v in versions:
                if 'fabric' in v['loaders'] and '1.21.1' in v['game_versions']:
                    print(v['version_number'] + " - " + v['files'][0]['url'])
    except Exception as e:
        print(e)

search_versions()
