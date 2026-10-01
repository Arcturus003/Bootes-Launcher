import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://addons-ecs.forgesvc.net/api/v2/addon/search?gameId=432&searchFilter=tensura-evolution-ui'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx) as response:
        print(response.read().decode())
except Exception as e:
    print(e)
