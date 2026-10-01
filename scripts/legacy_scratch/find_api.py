import urllib.request
import re

req = urllib.request.Request('https://skmedix.pl/downloads', headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    # look for any URL
    urls = re.findall(r'https://[^\'\" ]+', html)
    for u in set(urls):
        if 'api' in u or 'download' in u:
            print(u)
except Exception as e:
    pass
