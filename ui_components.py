from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QProgressBar, QSpacerItem, QSizePolicy, QFrame, QComboBox,
                               QListWidget, QListWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, Signal
import os

class ModItemWidget(QWidget):
    def __init__(self, filepath, parent_list):
        super().__init__()
        self.filepath = filepath
        self.parent_list = parent_list
        self.is_disabled = self.filepath.endswith(".disabled")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 25, 5) # Sağ margin'i artırdık (Scrollbar'ın butonları kapatmaması için)
        self.setMinimumHeight(50) # Widget'ın dikeyde ezilmesini kesin olarak önler
        
        filename = os.path.basename(self.filepath)
        if self.is_disabled:
            filename = filename[:-9] # remove .disabled
            
        self.name_lbl = QLabel(filename)
        self.name_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #EEE;")
        
        # Uzun isimlerin butonları sağa itmesini engellemek için:
        self.name_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        
        layout.addWidget(self.name_lbl, 1) # stretch=1
        
        self.toggle_btn = QPushButton("Açık" if not self.is_disabled else "Kapalı")
        self.toggle_btn.setFixedSize(90, 35) # 35px yükseklik ki yazılar dikeyde kesilmesin
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.update_toggle_style()
        self.toggle_btn.clicked.connect(lambda x=None: self.toggle_mod())
        layout.addWidget(self.toggle_btn)
        
        self.del_btn = QPushButton("Sil")
        self.del_btn.setFixedSize(50, 35)
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.setStyleSheet("background-color: #E53935; color: white; font-weight: bold; border-radius: 5px; font-size: 14px;")
        self.del_btn.clicked.connect(lambda x=None: self.delete_mod())
        layout.addWidget(self.del_btn)
        
    def update_toggle_style(self):
        if self.is_disabled:
            self.toggle_btn.setText("Kapalı")
            self.toggle_btn.setStyleSheet("background-color: #555; color: #AAA; border-radius: 5px; font-weight: bold; font-size: 14px;")
            self.name_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #888; text-decoration: line-through;")
        else:
            self.toggle_btn.setText("Açık")
            self.toggle_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; font-weight: bold; font-size: 14px;")
            self.name_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #EEE;")
            
    def toggle_mod(self):
        try:
            if self.is_disabled:
                new_path = self.filepath[:-9] # remove .disabled
                os.rename(self.filepath, new_path)
                self.filepath = new_path
                self.is_disabled = False
            else:
                new_path = self.filepath + ".disabled"
                os.rename(self.filepath, new_path)
                self.filepath = new_path
                self.is_disabled = True
            self.update_toggle_style()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Mod durumu değiştirilemedi:\n{e}")
            
    def delete_mod(self):
        reply = QMessageBox.question(self, 'Onay', "Bu modu silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(self.filepath)
                self.parent_list.refresh_list()
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Mod silinemedi:\n{e}")

class InstalledModsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InstalledModsPanel")
        self.current_dir = None
        self.pdata = None
        self.pid = None
        self.main_window = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        self.title = QLabel("Kurulu Modlar")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #40E0D0; margin-bottom: 10px;")
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        
        self.install_engine_btn = QPushButton("Oyun Motoru Kur (Forge/Fabric)")
        self.install_engine_btn.setCursor(Qt.PointingHandCursor)
        self.install_engine_btn.setStyleSheet("background-color: #8E2DE2; color: white; padding: 8px 15px; font-weight: bold; border-radius: 5px;")
        self.install_engine_btn.clicked.connect(self.open_engine_installer)
        self.install_engine_btn.hide() # Only show for Java profiles
        header_layout.addWidget(self.install_engine_btn)
        
        layout.addLayout(header_layout)
        
        self.mod_list = QListWidget()
        self.mod_list.setStyleSheet("QListWidget { background: rgba(30, 30, 30, 0.7); border: 1px solid #444; border-radius: 8px; outline: none; } QListWidget::item { border-bottom: 1px solid #333; padding: 5px; }")
        layout.addWidget(self.mod_list)
        
    def open_engine_installer(self):
        if not self.pdata or not self.main_window:
            return
        from engine_installer import EngineInstallDialog
        dialog = EngineInstallDialog(self.pdata, self.pid, self.main_window, self)
        dialog.exec()
        
    def load_mods(self, mods_dir, pdata=None, pid=None, main_window=None):
        self.current_dir = mods_dir
        self.pdata = pdata
        self.pid = pid
        self.main_window = main_window
        
        if pdata:
            self.install_engine_btn.show()
        else:
            self.install_engine_btn.hide()
            
        self.refresh_list()
        
    def refresh_list(self):
        self.mod_list.clear()
        if not self.current_dir or not os.path.exists(self.current_dir):
            item = QListWidgetItem("Bu profilde henüz mod yok.")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.NoItemFlags)
            self.mod_list.addItem(item)
            return
            
        mods = [f for f in os.listdir(self.current_dir) if f.endswith(".jar") or f.endswith(".jar.disabled") or f.endswith(".pak") or f.endswith(".pak.disabled")]
        
        if not mods:
            item = QListWidgetItem("Bu profilde henüz mod yok.")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.NoItemFlags)
            self.mod_list.addItem(item)
            return
            
        for mod in sorted(mods):
            path = os.path.join(self.current_dir, mod)
            item = QListWidgetItem(self.mod_list)
            widget = ModItemWidget(path, self)
            
            # Öğenin yüksekliğini sabit 50 piksel yapalım, böylece butonlar dikeyde ezilmez
            from PySide6.QtCore import QSize
            item.setSizeHint(QSize(100, 50))
            
            self.mod_list.setItemWidget(item, widget)

class NavButton(QPushButton):
    def __init__(self, icon_text, parent=None):
        super().__init__(icon_text, parent)
        self.setObjectName("NavButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)

class NavBar(QFrame):
    nav_clicked = Signal(str)
    game_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavBar")
        self.setFixedWidth(220)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(15)
        
        self.game_selector = QComboBox()
        self.game_selector.addItems(["Minecraft: Java Edition", "Minecraft for Windows", "Minecraft Dungeons"])
        self.game_selector.setStyleSheet("QComboBox { background-color: #2D2D30; color: white; padding: 10px; border-radius: 5px; font-size: 14px; font-weight: bold; }")
        self.game_selector.currentTextChanged.connect(self.on_game_change)
        layout.addWidget(self.game_selector)
        
        self.btns = {}
        tabs = {
            "home": "🏠 Profiller",
            "packs": "📦 Modpaketleri",
            "mods": "🧩 Modlar",
            "shaders": "✨ Shaderlar",
            "bedrock_home": "🏠 Oyna (Bedrock)",
            "dungeons_home": "🏠 Oyna (Dungeons)",
            "server": "🖥️ Sunucum"
        }
        
        for key, text in tabs.items():
            btn = NavButton(text)
            btn.clicked.connect(lambda checked=False, k=key: self.on_nav_click(k))
            self.btns[key] = btn
            layout.addWidget(btn)
            
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.on_game_change("Minecraft: Java Edition")

    def on_game_change(self, game_name):
        # Hide all first
        for btn in self.btns.values():
            btn.hide()
            
        if game_name == "Minecraft: Java Edition":
            self.btns["home"].show()
            self.btns["packs"].show()
            self.btns["mods"].show()
            self.btns["shaders"].show()
            self.btns["server"].show()
            self.btns["home"].click()
        elif game_name == "Minecraft for Windows":
            self.btns["bedrock_home"].show()
            self.btns["bedrock_home"].click()
        elif game_name == "Minecraft Dungeons":
            self.btns["dungeons_home"].show()
            self.btns["dungeons_home"].click()
            
        self.game_changed.emit(game_name)

    def on_nav_click(self, key):
        for k, b in self.btns.items():
            b.setProperty("active", str(k == key).lower())
            b.style().unpolish(b)
            b.style().polish(b)
        self.nav_clicked.emit(key)

class ActionBar(QFrame):
    play_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ActionBar")
        self.setFixedHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 10, 30, 10)
        
        self.info_layout = QVBoxLayout()
        self.pack_name = QLabel("Seçili Paket Yok")
        self.pack_name.setStyleSheet("font-size: 18px; font-weight: bold; color: white; background: transparent;")
        self.pack_size = QLabel("0 MB")
        self.pack_size.setStyleSheet("color: #AAAAAA; background: transparent;")
        self.info_layout.addWidget(self.pack_name)
        self.info_layout.addWidget(self.pack_size)
        layout.addLayout(self.info_layout)
        
        layout.addStretch()
        
        self.center_layout = QVBoxLayout()
        self.center_layout.setAlignment(Qt.AlignCenter)
        self.play_btn = QPushButton("OYNA")
        self.play_btn.setObjectName("PlayButton")
        self.play_btn.setCursor(Qt.PointingHandCursor)
        self.play_btn.clicked.connect(self.play_clicked.emit)
        self.center_layout.addWidget(self.play_btn)
        
        self.progress = QProgressBar()
        self.progress.setFixedSize(200, 4)
        self.progress.setVisible(False)
        self.center_layout.addWidget(self.progress)
        layout.addLayout(self.center_layout)
        
        layout.addStretch()
        
        right_layout = QHBoxLayout()
        self.folder_btn = QPushButton("📁 .minecraft")
        self.folder_btn.setStyleSheet("background: transparent; font-size: 16px; color: #888; border: none;")
        self.folder_btn.setCursor(Qt.PointingHandCursor)
        
        right_layout.addWidget(self.folder_btn)
        layout.addLayout(right_layout)
