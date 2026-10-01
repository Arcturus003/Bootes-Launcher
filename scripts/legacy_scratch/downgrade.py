import urllib.request
import os

url = 'https://cdn.modrinth.com/data/Br0kXPwc/versions/bot6zu0e/tensura-fabric-2.0.1.1.jar'
dest1 = r'C:\Users\Vega\AppData\Roaming\.tlauncher\legacy\Minecraft\game\mods\tensura-fabric-2.0.1.1.jar'
dest2 = r'C:\Users\Vega\Documents\antigravity\quick-pythagoras\profiles\Slimes Adventure\mods\tensura-fabric-2.0.1.1.jar'

old1 = r'C:\Users\Vega\AppData\Roaming\.tlauncher\legacy\Minecraft\game\mods\tensura-fabric-2.0.1.3.jar'
old2 = r'C:\Users\Vega\Documents\antigravity\quick-pythagoras\profiles\Slimes Adventure\mods\tensura-fabric-2.0.1.3.jar'

try:
    if os.path.exists(old1): os.remove(old1)
    if os.path.exists(old2): os.remove(old2)
except: pass

print('Downloading...')
urllib.request.urlretrieve(url, dest1)
urllib.request.urlretrieve(url, dest2)
print('Done!')
