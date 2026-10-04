# Yeni Sürüm Yayınlama (Nexus Client)

Uygulama açılışta `https://api.github.com/repos/Arcturus003/nexus-client/releases/latest`
adresini kontrol eder. Release etiketi (ör. `v1.1.0`) `main.py` içindeki `__version__`
değerinden büyükse kullanıcıya güncelleme sorulur, release'e eklenmiş `.exe` indirilir
ve sessizce kurulur, ardından uygulama yeniden açılır.

## Adımlar

1. **Sürümü artır** (iki yer de AYNI olmalı):
   - `main.py` → `__version__ = "1.1.0"`
   - `setup.iss` → `#define MyAppVersion "1.1.0"`
2. **Bütünlük hash'lerini yenile:**
   ```
   python integrity_check.py generate
   ```
3. **Derle:** PyInstaller ile `build_out\main\` klasörünü üret (build_nexus_client skill'i),
   sonra Inno Setup ile `setup.iss`'i derle → `build_out\NexusClient_Setup_v1.1.0.exe`.
4. **Commit + etiket + push:**
   ```
   git add -A
   git commit -m "v1.1.0"
   git tag v1.1.0
   git push origin main
   git push origin v1.1.0
   ```
   (Dal adınız `master` ise `main` yerine onu yazın: `git branch --show-current`.)
5. **GitHub Release oluştur:** github.com/Arcturus003/nexus-client → *Releases* →
   *Draft a new release* → etiket `v1.1.0` seç → `NexusClient_Setup_v1.1.0.exe` dosyasını
   ekle → **Publish release**. ("Pre-release" veya taslak release'ler kullanıcılara gösterilmez.)

## Notlar
- Etiket mutlaka `vX.Y.Z` biçiminde olmalı ve `__version__`'dan büyük olmalı.
- Release'e eklenen dosya `.exe` olmalı; adında `Setup` geçen dosya tercih edilir.
- İnternet yoksa veya GitHub API limiti (saatte 60 istek/IP) aşılırsa kontrol sessizce atlanır.
- `token.json`, `credentials.json`, `launcher_config.json` `.gitignore`'dadır; asla commit etmeyin.
