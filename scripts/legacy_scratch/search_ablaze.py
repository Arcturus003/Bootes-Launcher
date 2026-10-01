import urllib.request
import urllib.parse
import json

def search():
    query = urllib.parse.quote('AblazeAQZL')
    url = f'https://api.modrinth.com/v2/search?query={query}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Antigravity/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            for hit in data['hits']:
                print(hit['title'] + " - " + hit['project_id'])
    except Exception as e:
        print(e)

search()
