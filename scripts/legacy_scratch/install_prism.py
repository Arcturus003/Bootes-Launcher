import urllib.request, json, os, zipfile, io

req = urllib.request.Request('https://api.github.com/repos/PrismLauncher/PrismLauncher/releases/latest')
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    zip_url = None
    for asset in data.get('assets', []):
        if 'MSVC-Windows-x86_64' in asset['name'] and asset['name'].endswith('.zip'):
            zip_url = asset['browser_download_url']
            break

if zip_url:
    print("Downloading PrismLauncher from:", zip_url)
    zip_req = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(zip_req) as z_resp:
        z_data = z_resp.read()
    
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop', 'PrismLauncher')
    os.makedirs(desktop, exist_ok=True)
    
    with zipfile.ZipFile(io.BytesIO(z_data)) as z:
        z.extractall(desktop)
    
    # Create accounts.json for offline mode
    accounts = {
        "accounts": [
            {
                "entitlement": {
                    "canPlayMinecraft": True,
                    "ownsMinecraft": True
                },
                "profile": {
                    "capes": [],
                    "id": "00000000000000000000000000000000",
                    "name": "TestOyuncu",
                    "skins": []
                },
                "type": "Offline"
            }
        ],
        "formatVersion": 3
    }
    
    # Prism saves it in /accounts.json
    with open(os.path.join(desktop, 'accounts.json'), 'w') as f:
        json.dump(accounts, f, indent=4)
        
    print("Prism Launcher installed and Offline Account configured at Desktop/PrismLauncher")
else:
    print("Could not find portable zip")
