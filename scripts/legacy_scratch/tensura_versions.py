import urllib.request
import json

def get_versions():
    # project id for tensura-reincarnated is ZQO5H2s4 usually? Let's search again.
    search_url = 'https://api.modrinth.com/v2/search?query=Tensura:%20Reincarnated'
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Antigravity/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            p_id = data['hits'][0]['project_id']
            
            v_url = f'https://api.modrinth.com/v2/project/{p_id}/version'
            v_req = urllib.request.Request(v_url, headers={'User-Agent': 'Antigravity/1.0'})
            with urllib.request.urlopen(v_req) as v_res:
                versions = json.loads(v_res.read().decode())
                for v in versions:
                    if 'fabric' in v['loaders'] and '1.21.1' in v['game_versions']:
                        print(f"{v['version_number']} - {v['files'][0]['url']}")
    except Exception as e:
        print(e)
get_versions()
