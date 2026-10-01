import urllib.request
import urllib.parse
import json

def get_latest_version(query):
    query_encoded = urllib.parse.quote(query)
    search_url = f'https://api.modrinth.com/v2/search?query={query_encoded}&facets=[[%22categories:fabric%22],[%22versions:1.21.1%22]]'
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Antigravity/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data['hits']:
                project_id = data['hits'][0]['project_id']
                versions_url = f'https://api.modrinth.com/v2/project/{project_id}/version'
                v_req = urllib.request.Request(versions_url, headers={'User-Agent': 'Antigravity/1.0'})
                with urllib.request.urlopen(v_req) as v_response:
                    versions = json.loads(v_response.read().decode())
                    for v in versions:
                        if 'fabric' in v['loaders'] and '1.21.1' in v['game_versions']:
                            file = v['files'][0]
                            return {
                                'name': data['hits'][0]['title'],
                                'version': v['version_number'],
                                'url': file['url'],
                                'filename': file['filename']
                            }
    except Exception as e:
        return {'error': str(e)}
    return None

queries = ['tensura ep scaling', 'tensura kumodesu', 'tensura neb', 'tensura opac', 'tensura unique monsters', 'tensura better subs']
results = {}
for q in queries:
    results[q] = get_latest_version(q)

print(json.dumps(results, indent=2))
