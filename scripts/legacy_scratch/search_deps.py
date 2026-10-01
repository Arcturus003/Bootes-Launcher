import urllib.request
import urllib.parse
import json

def get_latest_version(query, project_id=None):
    if project_id:
        p_id = project_id
        title = query
    else:
        query_encoded = urllib.parse.quote(query)
        search_url = f'https://api.modrinth.com/v2/search?query={query_encoded}&facets=[[%22categories:fabric%22],[%22versions:1.21.1%22]]'
        try:
            req = urllib.request.Request(search_url, headers={'User-Agent': 'Antigravity/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if data['hits']:
                    p_id = data['hits'][0]['project_id']
                    title = data['hits'][0]['title']
                else:
                    return None
        except Exception as e:
            return {'error': str(e)}

    versions_url = f'https://api.modrinth.com/v2/project/{p_id}/version'
    try:
        v_req = urllib.request.Request(versions_url, headers={'User-Agent': 'Antigravity/1.0'})
        with urllib.request.urlopen(v_req) as v_response:
            versions = json.loads(v_response.read().decode())
            for v in versions:
                if 'fabric' in v['loaders'] and '1.21.1' in v['game_versions']:
                    file = v['files'][0]
                    return {
                        'name': title,
                        'version': v['version_number'],
                        'url': file['url'],
                        'filename': file['filename']
                    }
    except Exception as e:
        return {'error': str(e)}
    return None

queries = [
    ('GeckoLib', '8BmcQJ2H'), 
    ('ManasCore', 'qV80n0c2'), # Wait, I don't know ManasCore ID, I'll let it search
    ('SmartBrainLib', None)
]

results = {}
for q, pid in queries:
    results[q] = get_latest_version(q, pid)
    
results['ManasCore'] = get_latest_version('ManasCore')

print(json.dumps(results, indent=2))
