import urllib.request, json
# Find Slimes Adventure project ID
url = 'https://api.modrinth.com/v2/search?query=Slimes%20Adventure&facets=[[%22project_type:modpack%22]]'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    for hit in data['hits']:
        if hit['title'] == 'Slimes Adventure':
            project_id = hit['project_id']
            print(f"Project ID: {project_id}")
            # Get latest versions
            v_url = f'https://api.modrinth.com/v2/project/{project_id}/version'
            v_req = urllib.request.Request(v_url, headers={'User-Agent': 'Mozilla/5.0'})
            v_resp = urllib.request.urlopen(v_req)
            v_data = json.loads(v_resp.read().decode('utf-8'))
            for v in v_data:
                if '1.21.1' in v['game_versions']:
                    print(f"Version {v['version_number']} supports 1.21.1 with loaders: {v['loaders']}")
            break
except Exception as e:
    print(e)
