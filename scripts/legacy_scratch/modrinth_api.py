import urllib.request, json
url = 'https://api.modrinth.com/v2/search?query=Tensura&facets=[[%22project_type:modpack%22]]'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    for hit in data['hits']:
        print(f"{hit['title']} - Downloads: {hit['downloads']} - Versions: {hit['versions']}")
except Exception as e:
    print(e)
