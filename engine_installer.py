import os
import minecraft_launcher_lib
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QProgressBar, QMessageBox)
from PySide6.QtCore import QThread, Signal

class EngineInstallThread(QThread):
    progress_update = Signal(int, int, str)
    finished_install = Signal(bool, str) # success, version_id_or_error

    def __init__(self, engine_type, mc_version, mc_dir):
        super().__init__()
        self.engine_type = engine_type
        self.mc_version = mc_version
        self.mc_dir = mc_dir
        
    def run(self):
        try:
            callback = {
                "setStatus": lambda text: self.progress_update.emit(0, 0, text),
                "setProgress": lambda progress: self.progress_update.emit(progress, 100, ""),
                "setMax": lambda max_val: None
            }
            
            if self.engine_type == "Fabric":
                loader_ver = minecraft_launcher_lib.fabric.get_latest_loader_version()
                minecraft_launcher_lib.fabric.install_fabric(self.mc_version, self.mc_dir, loader_version=loader_ver, callback=callback)
                new_version_id = f"fabric-loader-{loader_ver}-{self.mc_version}"
                self.finished_install.emit(True, new_version_id)
                
            elif self.engine_type == "Forge":
                forge_ver = minecraft_launcher_lib.forge.find_forge_version(self.mc_version)
                if not forge_ver:
                    self.finished_install.emit(False, f"Forge {self.mc_version} için bulunamadı.")
                    return
                minecraft_launcher_lib.forge.install_forge_version(forge_ver, self.mc_dir, callback=callback)
                
                # Orijinal forge adını bul
                # Genelde 1.20.1-forge-47.4.5 gibi olur. Klasörleri tarayarak bulalım.
                versions_dir = os.path.join(self.mc_dir, "versions")
                found = None
                if os.path.exists(versions_dir):
                    # En yeni oluşturulan forge klasörünü bulalım
                    forge_dirs = []
                    for d in os.listdir(versions_dir):
                        if "forge" in d.lower() and self.mc_version in d:
                            dpath = os.path.join(versions_dir, d)
                            if os.path.isdir(dpath):
                                forge_dirs.append((d, os.path.getmtime(dpath)))
                    if forge_dirs:
                        forge_dirs.sort(key=lambda x: x[1], reverse=True)
                        found = forge_dirs[0][0]
                            
                if found:
                    self.finished_install.emit(True, found)
                else:
                    self.finished_install.emit(False, "Kurulum tamamlandı fakat versiyon ID'si bulunamadı.")
            elif self.engine_type == "NeoForge":
                try:
                    import minecraft_launcher_lib.mod_loader
                    neo = minecraft_launcher_lib.mod_loader.get_mod_loader('neoforge')
                    latest_neo = neo.get_latest_loader_version(self.mc_version)
                    if not latest_neo:
                        self.finished_install.emit(False, f"NeoForge {self.mc_version} için bulunamadı veya desteklenmiyor.")
                        return
                    
                    self.progress_update.emit(0, 100, f"NeoForge {latest_neo} indiriliyor...")
                    installed_ver = neo.install(self.mc_version, latest_neo, self.mc_dir, callback=callback)
                    if not installed_ver:
                        installed_ver = neo.get_installed_version(self.mc_version, latest_neo)
                    self.finished_install.emit(True, installed_ver)
                except minecraft_launcher_lib.exceptions.UnsupportedVersion:
                    self.finished_install.emit(False, f"NeoForge, {self.mc_version} sürümünü desteklemiyor.")
                    
        except Exception as e:
            self.finished_install.emit(False, str(e))

class EngineInstallDialog(QDialog):
    def __init__(self, profile_data, profile_id, main_window, parent=None):
        super().__init__(parent)
        self.profile_data = profile_data
        self.profile_id = profile_id
        self.main_window = main_window # To update config and UI
        
        # Orijinal sürüm adını al (örn: 1.20.1, fabric-loader-0.14.22-1.20.1 vb.)
        self.current_version = profile_data.get("version", "")
        # Saf minecraft sürümünü ayıkla (eğer zaten fabric/forge ise baz versiyonu bulur)
        self.base_mc_version = self.extract_base_version(self.current_version)
        
        self.setWindowTitle(f"Motor Kurucu - {profile_data.get('name')}")
        self.setFixedSize(450, 250)
        self.setStyleSheet("background-color: #252526; color: white;")
        
        layout = QVBoxLayout(self)
        
        info_lbl = QLabel(f"Oyun Sürümü: {self.base_mc_version}")
        info_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #40E0D0;")
        layout.addWidget(info_lbl)
        
        desc = QLabel("Bu profile kurulacak motoru (Loader) seçin.\nMotorlar harici modları (.jar) çalıştırmanızı sağlar.")
        desc.setStyleSheet("color: #CCC;")
        layout.addWidget(desc)
        
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Fabric", "Forge", "NeoForge"])
        self.engine_combo.setStyleSheet("padding: 8px; font-size: 14px; background: #333; color: white; border-radius: 5px;")
        layout.addWidget(self.engine_combo)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #555; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #40E0D0; }")
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #888;")
        layout.addWidget(self.status_lbl)
        
        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Kur")
        self.install_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.install_btn.clicked.connect(self.start_install)
        btn_layout.addWidget(self.install_btn)
        
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.setStyleSheet("background-color: #E53935; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def extract_base_version(self, ver_str):
        import re
        match = re.search(r'(\d+\.\d+(?:\.\d+)?)', ver_str)
        if match:
            return match.group(1)
        return ver_str

    def start_install(self):
        engine = self.engine_combo.currentText()
        mc_dir = self.main_window.mc_dir
        
        self.install_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.engine_combo.setEnabled(False)
        self.progress_bar.show()
        
        self.thread = EngineInstallThread(engine, self.base_mc_version, mc_dir)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.finished_install.connect(self.on_install_finished)
        self.thread.start()
        
        # Keep reference to prevent GC
        self.main_window._api_threads = getattr(self.main_window, '_api_threads', [])
        self.main_window._api_threads.append(self.thread)
        
    def update_progress(self, current, total, text):
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
        if text:
            self.status_lbl.setText(text)
            
    def on_install_finished(self, success, result):
        if success:
            QMessageBox.information(self, "Başarılı", f"Motor başarıyla kuruldu!\nYeni Sürüm: {result}")
            # Update config and UI
            self.main_window.profiles[self.profile_id]["version"] = result
            self.main_window.profiles[self.profile_id]["loader"] = self.engine_combo.currentText().lower()
            self.main_window.save_config()
            self.main_window.on_profile_selected() 
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", f"Kurulum başarısız oldu:\n{result}")
            self.install_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            self.engine_combo.setEnabled(True)
            self.progress_bar.hide()
            self.status_lbl.setText("Hata oluştu.")
