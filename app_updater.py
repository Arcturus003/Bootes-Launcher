"""GitHub Releases tabanli otomatik guncelleme.

Akis: arka planda (QThread) latest release sorgulanir -> surum yeniyse kullaniciya
sorulur -> .exe asset'i ilerleme ile indirilir -> Inno Setup sessiz modda
calistirilir -> uygulama kapanir. Setup bittikten sonra setup.iss [Run]
bolumu uygulamayi yeniden baslatir.
Cevrimdisi / rate-limit / herhangi bir hata durumunda sessizce hicbir sey yapmaz.
"""
import os
import re
import sys
import json
import tempfile
import urllib.request

from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QApplication

GITHUB_REPO = "Arcturus003/Vega-Launcher"
LATEST_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
USER_AGENT = "VegaLauncher-Updater"


def parse_version(text):
    """'v1.2.3' / '1.2' / '1.2.3-beta' -> (1, 2, 3). Gecersizse None."""
    if not text:
        return None
    m = re.match(r"^\s*v?(\d+(?:\.\d+)*)", str(text))
    if not m:
        return None
    parts = [int(p) for p in m.group(1).split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_newer(remote, local):
    r, l = parse_version(remote), parse_version(local)
    if r is None or l is None:
        return False
    n = max(len(r), len(l))
    r = r + (0,) * (n - len(r))
    l = l + (0,) * (n - len(l))
    return r > l


def pick_installer_asset(release):
    """Release icinden kurulum .exe'sini sec (Setup iceren tercih edilir)."""
    assets = [a for a in (release.get("assets") or [])
              if str(a.get("name", "")).lower().endswith(".exe") and a.get("browser_download_url")]
    if not assets:
        return None
    for a in assets:
        if "setup" in a["name"].lower():
            return a
    return assets[0]


class UpdateCheckThread(QThread):
    update_available = Signal(str, str, str, int)  # tag, url, name, size

    def __init__(self, current_version, parent=None):
        super().__init__(parent)
        self.current_version = current_version

    def run(self):
        try:
            req = urllib.request.Request(LATEST_URL, headers={
                "User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                release = json.loads(resp.read().decode("utf-8"))
            if release.get("draft") or release.get("prerelease"):
                return
            tag = release.get("tag_name", "")
            if not is_newer(tag, self.current_version):
                return
            asset = pick_installer_asset(release)
            if not asset:
                return
            self.update_available.emit(tag, asset["browser_download_url"],
                                       asset["name"], int(asset.get("size") or 0))
        except Exception as e:  # offline, 403 rate limit, JSON hatasi...
            print(f"[Updater] Guncelleme kontrolu atlandi: {e}")


class UpdateDownloadThread(QThread):
    progress = Signal(int)            # 0-100, bilinmiyorsa -1
    download_finished = Signal(bool, str)  # basari, dosya yolu / hata mesaji

    def __init__(self, url, filename, parent=None):
        super().__init__(parent)
        self.url = url
        self.filename = os.path.basename(filename) or "VegaLauncher_Setup.exe"
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        dest = os.path.join(tempfile.gettempdir(), self.filename)
        part = dest + ".part"
        try:
            req = urllib.request.Request(self.url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp, open(part, "wb") as f:
                total = int(resp.headers.get("Content-Length") or 0)
                done = 0
                while True:
                    if self._cancel:
                        raise RuntimeError("Iptal edildi")
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    self.progress.emit(int(done * 100 / total) if total else -1)
            if total and done != total:
                raise RuntimeError("Indirme eksik kaldi")
            if os.path.exists(dest):
                os.remove(dest)
            os.replace(part, dest)
            self.download_finished.emit(True, dest)
        except Exception as e:
            try:
                if os.path.exists(part):
                    os.remove(part)
            except Exception:
                pass
            self.download_finished.emit(False, str(e))


def launch_installer(path):
    """Kurulumu sessiz baslat. ShellExecute UAC yukseltmesini destekler."""
    args = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS /SP-"
    if sys.platform == "win32":
        import ctypes
        rc = ctypes.windll.shell32.ShellExecuteW(None, "open", path, args, None, 1)
        return rc > 32
    return False


class AppUpdater(QObject):
    """Ana pencereye bagli guncelleyici. Thread referanslarini tutar."""

    def __init__(self, parent_window, current_version):
        super().__init__(parent_window)
        self.window = parent_window
        self.current_version = current_version
        self._threads = []
        self._progress_dialog = None

    def _keep(self, t):
        self._threads.append(t)
        t.finished.connect(lambda t=t: self._threads.remove(t) if t in self._threads else None)

    def check(self):
        t = UpdateCheckThread(self.current_version)
        t.update_available.connect(self._on_update_available)
        self._keep(t)
        t.start()

    def _on_update_available(self, tag, url, name, size):
        size_txt = f" ({size / 1024 / 1024:.1f} MB)" if size else ""
        ans = QMessageBox.question(
            self.window, "Güncelleme",
            f"Yeni sürüm var ({tag}){size_txt}. Şimdi güncellensin mi?\n\n"
            f"Mevcut sürüm: v{self.current_version}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ans != QMessageBox.Yes:
            return
        dlg = QProgressDialog("Güncelleme indiriliyor...", "İptal", 0, 100, self.window)
        dlg.setWindowTitle("Vega Launcher Güncelleme")
        dlg.setWindowModality(Qt.WindowModal)
        dlg.setMinimumDuration(0)
        dlg.setAutoClose(False)
        dlg.setAutoReset(False)
        dlg.setValue(0)
        self._progress_dialog = dlg

        t = UpdateDownloadThread(url, name)
        t.progress.connect(self._on_progress)
        t.download_finished.connect(self._on_download_finished)
        dlg.canceled.connect(t.cancel)
        self._keep(t)
        t.start()
        dlg.show()

    def _on_progress(self, pct):
        dlg = self._progress_dialog
        if not dlg:
            return
        if pct < 0:
            dlg.setRange(0, 0)
        else:
            dlg.setRange(0, 100)
            dlg.setValue(pct)

    def _on_download_finished(self, ok, result):
        dlg, self._progress_dialog = self._progress_dialog, None
        was_canceled = dlg.wasCanceled() if dlg else False
        if dlg:
            dlg.close()
        if not ok:
            if not was_canceled:
                QMessageBox.warning(self.window, "Güncelleme",
                                    f"Güncelleme indirilemedi:\n{result}")
            return
        if not launch_installer(result):
            QMessageBox.warning(self.window, "Güncelleme",
                                f"Kurulum başlatılamadı. Elle çalıştırabilirsiniz:\n{result}")
            return
        # Kurulum dosyalari degistirebilsin diye uygulamayi kapat.
        self.window.close()
        QApplication.instance().quit()
