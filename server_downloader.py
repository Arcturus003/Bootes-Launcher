import os
import urllib.request
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, 
                               QPushButton, QProgressBar, QMessageBox)

_active_download_threads = []

class ServerDownloadThread(QThread):
    progress = Signal(int)
    log_msg = Signal(str)
    finished_dl = Signal(bool)

    def __init__(self, software, version, target_path, parent=None):
        super().__init__(parent)
        self.software = software
        self.version = version
        self.target_path = target_path
        self.is_downloading = False

    def run(self):
        self.is_downloading = True
        try:
            url = ""
            is_installer = False
            if self.software == "Purpur (Eklenti)":
                url = f"https://api.purpurmc.org/v2/purpur/{self.version}/latest/download"
            elif self.software == "Fabric (Mod)":
                import json
                self.log_msg.emit("Fabric meta verileri alınıyor...")
                req_meta = urllib.request.Request("https://meta.fabricmc.net/v2/versions/loader", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_meta, timeout=15) as meta_resp:
                    meta_json = json.loads(meta_resp.read().decode('utf-8'))
                    latest_loader = next(item["version"] for item in meta_json if item.get("stable"))
                url = f"https://meta.fabricmc.net/v2/versions/loader/{self.version}/{latest_loader}/1.0.1/server/jar"
            elif self.software == "Forge (Mod)":
                import json
                self.log_msg.emit("Forge sürüm verileri alınıyor...")
                req_forge = urllib.request.Request("https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_forge, timeout=15) as forge_resp:
                    forge_data = json.loads(forge_resp.read().decode('utf-8'))
                    promos = forge_data.get("promos", {})
                    forge_version = promos.get(f"{self.version}-recommended") or promos.get(f"{self.version}-latest")
                    if not forge_version:
                        self.log_msg.emit(f"[HATA] {self.version} için Forge sürümü bulunamadı.")
                        self.finished_dl.emit(False)
                        self.is_downloading = False
                        return
                    url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{self.version}-{forge_version}/forge-{self.version}-{forge_version}-installer.jar"
                is_installer = True
            elif self.software == "NeoForge (Mod)":
                import json
                self.log_msg.emit("NeoForge sürüm verileri alınıyor...")
                req_neo = urllib.request.Request("https://maven.neoforged.net/api/maven/versions/releases/net/neoforged/neoforge", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_neo, timeout=15) as neo_resp:
                    neo_data = json.loads(neo_resp.read().decode('utf-8'))
                    versions = neo_data.get("versions", [])
                    if self.version == "1.21.1": prefix = "21.1."
                    elif self.version == "1.21": prefix = "21.0."
                    elif self.version == "1.20.4": prefix = "20.4."
                    elif self.version == "1.20.2": prefix = "20.2."
                    else:
                        self.log_msg.emit(f"[HATA] {self.version} için NeoForge sürümü desteklenmiyor.")
                        self.finished_dl.emit(False)
                        self.is_downloading = False
                        return
                    valid_versions = [v for v in versions if v.startswith(prefix)]
                    if not valid_versions:
                        self.log_msg.emit(f"[HATA] {self.version} için NeoForge sürümü bulunamadı.")
                        self.finished_dl.emit(False)
                        self.is_downloading = False
                        return
                    valid_versions.sort(key=lambda x: [int(p) for p in x.split('.') if p.isdigit()])
                    latest = valid_versions[-1]
                    url = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{latest}/neoforge-{latest}-installer.jar"
                is_installer = True
            else:
                self.log_msg.emit("[HATA] Desteklenmeyen yazılım.")
                self.finished_dl.emit(False)
                self.is_downloading = False
                return

            self.log_msg.emit(f"[BİLGİ] İndiriliyor: {self.software} {self.version}")
            
            download_path = os.path.join(os.path.dirname(self.target_path), "installer.jar") if is_installer else self.target_path
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                total_size = int(response.getheader('Content-Length', 0))
                downloaded = 0
                chunk_size = 8192
                with open(download_path, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress.emit(int(downloaded * 100 / total_size))
                            
            if is_installer:
                self.log_msg.emit(f"[BİLGİ] {self.software} kuruluyor, lütfen bekleyin...")
                import subprocess
                server_dir = os.path.dirname(self.target_path)
                installer_path = os.path.join(server_dir, "installer.jar")
                try:
                    process = subprocess.Popen(
                        ["java", "-jar", installer_path, "--installServer"],
                        cwd=server_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            # Keep log short to avoid UI lag, just show the last part or generic progress
                            self.log_msg.emit(f"Kurulum: {line.strip()[:80]}")
                    process.wait()
                    if process.returncode == 0:
                        self.log_msg.emit(f"[BİLGİ] {self.software} kurulumu tamamlandı.")
                        # Rename forge jar to server.jar if it exists (for < 1.17 versions)
                        for f in os.listdir(server_dir):
                            if f.startswith("forge-") and f.endswith(".jar") and f != "installer.jar":
                                try:
                                    os.replace(os.path.join(server_dir, f), os.path.join(server_dir, "server.jar"))
                                    break
                                except: pass
                    else:
                        self.log_msg.emit(f"[HATA] {self.software} kurulumu başarısız oldu (Kod: {process.returncode}).")
                        self.finished_dl.emit(False)
                        self.is_downloading = False
                        return
                except FileNotFoundError:
                    self.log_msg.emit("[HATA] Sistemde Java bulunamadı. Lütfen Java yükleyin.")
                    self.finished_dl.emit(False)
                    self.is_downloading = False
                    return
                except Exception as e:
                    self.log_msg.emit(f"[HATA] Yükleyici çalıştırılamadı: {e}")
                    self.finished_dl.emit(False)
                    self.is_downloading = False
                    return
                finally:
                    if os.path.exists(installer_path):
                        try: os.remove(installer_path)
                        except: pass
            
            # --- Otomatik Playit.gg İndirme Mantığı ---
            self.log_msg.emit("Playit.gg altyapısı indiriliyor...")
            try:
                import json
                playit_url = ""
                dest_folder = ""
                
                if self.software == "Purpur (Eklenti)":
                    playit_url = "https://github.com/playit-cloud/playit-minecraft-plugin/releases/latest/download/playit-minecraft-plugin.jar"
                    dest_folder = "plugins"
                elif self.software in ("Fabric (Mod)", "Forge (Mod)", "NeoForge (Mod)"):
                    loader_id = "fabric"
                    if self.software == "Forge (Mod)": loader_id = "forge"
                    elif self.software == "NeoForge (Mod)": loader_id = "neoforge"
                    
                    req_playit = urllib.request.Request(f"https://api.modrinth.com/v2/project/playit-companion/version?game_versions=[%22{self.version}%22]&loaders=[%22{loader_id}%22]", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_playit, timeout=15) as playit_resp:
                        playit_json = json.loads(playit_resp.read().decode('utf-8'))
                        if playit_json:
                            playit_url = playit_json[0]["files"][0]["url"]
                    dest_folder = "mods"
                
                if playit_url and dest_folder:
                    server_dir = os.path.dirname(self.target_path)
                    os.makedirs(os.path.join(server_dir, dest_folder), exist_ok=True)
                    playit_target = os.path.join(server_dir, dest_folder, f"playit-{self.software.split(' ')[0].lower()}.jar")
                    
                    req_dl = urllib.request.Request(playit_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_dl, timeout=15) as response:
                        with open(playit_target, 'wb') as f:
                            f.write(response.read())
                    self.log_msg.emit("[BİLGİ] Playit.gg başarıyla kuruldu.")
            except Exception as pe:
                self.log_msg.emit(f"[UYARI] Playit.gg otomatik indirilemedi: {pe}")
            # ------------------------------------------
            
            self.progress.emit(100)
            self.log_msg.emit("[BİLGİ] Yazılım başarıyla indirildi ve kuruldu!")
            self.finished_dl.emit(True)
            
        except Exception as e:
            self.log_msg.emit(f"[HATA] İndirme başarısız: {e}")
            self.finished_dl.emit(False)
        finally:
            self.is_downloading = False

class ServerSoftwareDialog(QDialog):
    def __init__(self, parent=None, server_dir=None, auto_software=None, auto_version=None):
        super().__init__(parent)
        from PySide6.QtCore import Qt
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.server_dir = server_dir
        self.dl_thread = None
        self.setWindowTitle("Yazılım / Motor Değiştir")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background-color: #2D2D30; color: white;")
        
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Sunucu Yazılımı (Mod/Eklenti Altyapısı):")
        layout.addWidget(lbl)
        
        self.combo_software = QComboBox()
        self.combo_software.addItems(["Purpur (Eklenti)", "Fabric (Mod)", "Forge (Mod)", "NeoForge (Mod)"])
        self.combo_software.setStyleSheet("padding: 5px; background: #1E1E1E;")
        layout.addWidget(self.combo_software)
        
        lbl2 = QLabel("Sürüm:")
        layout.addWidget(lbl2)
        
        self.combo_version = QComboBox()
        self.combo_version.addItems(["1.21.1", "1.21", "1.20.4", "1.20.2", "1.20.1", "1.20", "1.19.4", "1.19.2", "1.18.2", "1.17.1", "1.16.5"])
        self.combo_version.setStyleSheet("padding: 5px; background: #1E1E1E;")
        layout.addWidget(self.combo_version)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)
        
        self.btn_install = QPushButton("🚀 Yazılımı Kur")
        self.btn_install.setStyleSheet("background-color: #007ACC; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_install.clicked.connect(self.install_software)
        layout.addWidget(self.btn_install)

        if auto_version:
            if self.combo_version.findText(auto_version) == -1:
                self.combo_version.addItem(auto_version)
            self.combo_version.setCurrentText(auto_version)
            
        if auto_software:
            self.combo_software.setCurrentText(auto_software)
            
        if auto_version and auto_software:
            lbl.hide()
            self.combo_software.hide()
            lbl2.hide()
            self.combo_version.hide()
            self.btn_install.hide()
            self.setFixedSize(400, 100)
            self.setWindowTitle("Otomatik Kurulum")
            
            from PySide6.QtCore import QTimer
            self._auto_install_timer = QTimer(self)
            self._auto_install_timer.setSingleShot(True)
            self._auto_install_timer.timeout.connect(self.install_software)
            self._auto_install_timer.start(500)
        
    def closeEvent(self, event):
        if self.dl_thread and self.dl_thread.is_downloading:
            QMessageBox.warning(self, "Uyarı", "İndirme işlemi devam ediyor, lütfen bekleyin!")
            event.ignore()
        else:
            event.accept()
            
    def install_software(self):
        if not self.server_dir:
            self.lbl_status.setText("Geçerli bir sunucu seçili değil!")
            return
            
        software = self.combo_software.currentText()
        version = self.combo_version.currentText()
        target_jar = os.path.join(self.server_dir, "server.jar")
        
        self.btn_install.setEnabled(False)
        self.lbl_status.setText(f"{software} {version} indiriliyor...")
        self.progress.setValue(0)
        
        self.dl_thread = ServerDownloadThread(software, version, target_jar, parent=None)
        
        # Rule 3: Keep strong reference in main UI class and module-level registry
        global _active_download_threads
        _active_download_threads = [t for t in _active_download_threads if t.isRunning()]
        _active_download_threads.append(self.dl_thread)

        parent_widget = self.parent()
        if hasattr(parent_widget, '_api_threads'):
            parent_widget._api_threads = [t for t in parent_widget._api_threads if t.isRunning()]
            parent_widget._api_threads.append(self.dl_thread)
            
        self.dl_thread.progress.connect(self.progress.setValue)
        self.dl_thread.log_msg.connect(self.lbl_status.setText)
        self.dl_thread.finished_dl.connect(self.on_finished)
        self.dl_thread.start()
        
    def on_finished(self, success):
        self.btn_install.setEnabled(True)
        if success:
            QMessageBox.information(self, "Başarılı", "Yazılım başarıyla güncellendi!\nMods veya Plugins klasörünüzü kontrol edebilirsiniz.")
            self.accept()
        else:
            if not self.btn_install.isVisible():
                QMessageBox.warning(self, "Hata", "Kurulum başarısız oldu veya desteklenmeyen yazılım.")
                self.reject()
