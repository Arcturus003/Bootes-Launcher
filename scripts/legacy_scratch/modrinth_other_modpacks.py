import urllib.request, json
urls = [
    'https://api.modrinth.com/v2/search?query=JACK%27s%20Tensura&facets=[[%22project_type:modpack%22]]',
    'https://api.modrinth.com/v2/search?query=TR%20world&facets=[[%22project_type:modpack%22]]',
    'https://api.modrinth.com/v2/search?query=Tensura%20Ultimate&facets=[[%22project_type:modpack%22]]',
    'https://api.modrinth.com/v2/search?query=Tensura%20Tempest&facets=[[%22project_type:modpack%22]]'
]
for url in urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode('utf-8'))
        for hit in data['hits']:
            print(f"{hit['title']} - Downloads: {hit['downloads']} - Versions: {hit['versions']}")
    except Exception as e:
        pass
