import urllib.request, json
# Find Great Sage project ID
url = 'https://api.modrinth.com/v2/search?query=Great%20Sage%20Tensura'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    for hit in data['hits']:
        print(f"{hit['title']} - ID: {hit['project_id']}")
except Exception as e:
    print(e)
