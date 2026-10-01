import urllib.request
import urllib.parse
import json

def search():
    query = urllib.parse.quote('TenSura Evolution UI')
    url = f'https://api.modrinth.com/v2/search?query={query}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Antigravity/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data['hits']:
                pid = data['hits'][0]['project_id']
                v_url = f'https://api.modrinth.com/v2/project/{pid}/version'
                v_req = urllib.request.Request(v_url, headers={'User-Agent': 'Antigravity/1.0'})
                with urllib.request.urlopen(v_req) as v_res:
                    versions = json.loads(v_res.read().decode())
                    for v in versions:
                        if 'fabric' in v['loaders'] and '1.21.1' in v['game_versions']:
                            print(v['files'][0]['url'])
                            return
    except Exception as e:
        print(e)

search()
