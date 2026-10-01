from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap
import requests

class ImageLoaderThread(QThread):
    loaded = Signal(bytes)
    loaded_with_url = Signal(str, bytes)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        try:
            resp = requests.get(self.url, timeout=5)
            if resp.status_code == 200:
                self.loaded.emit(resp.content)
                self.loaded_with_url.emit(self.url, resp.content)
        except Exception:
            pass

class CardWidget(QFrame):
    clicked = Signal(object)
    update_clicked = Signal(object)
    _active_threads = set()
    
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setObjectName("ModpackCard")
        self.setFixedSize(220, 180)
        self.setCursor(Qt.PointingHandCursor)
        self.img_thread = None
        self.destroyed.connect(lambda obj=None: self.cleanup())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header (Icon + Title)
        header_layout = QHBoxLayout()
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(48, 48)
        self.icon_lbl.setStyleSheet("background-color: transparent;")
        header_layout.addWidget(self.icon_lbl)
        
        self.title = QLabel(data.get("title", "İsimsiz"))
        self.title.setObjectName("CardTitle")
        self.title.setWordWrap(True)
        header_layout.addWidget(self.title, 1, Qt.AlignVCenter)
        
        layout.addLayout(header_layout)
        
        # Desc
        self.desc = QLabel(data.get("description", ""))
        self.desc.setObjectName("CardSubtitle")
        self.desc.setWordWrap(True)
        layout.addWidget(self.desc)
        
        layout.addStretch()
        
        # Bottom info (version etc)
        versions = data.get("versions", [])
        v_text = versions[-1] if versions else "Unknown"
        self.version = QLabel(f"Sürüm: {v_text}")
        self.version.setObjectName("CardSubtitle")
        layout.addWidget(self.version)
        
        from PySide6.QtWidgets import QPushButton
        self.update_btn = QPushButton("Güncelleme Mevcut")
        self.update_btn.setStyleSheet("background-color: #FFA500; color: black; font-weight: bold; border-radius: 4px; padding: 4px;")
        self.update_btn.setVisible(False)
        self.update_btn.clicked.connect(lambda checked=False: self.update_clicked.emit(self.data) if hasattr(self, 'update_clicked') else None)
        layout.addWidget(self.update_btn)
        
        # Load Icon
        icon_url = data.get("icon_url")
        if icon_url:
            self.img_thread = ImageLoaderThread(icon_url)
            CardWidget._active_threads.add(self.img_thread)
            self.img_thread.loaded.connect(self.set_icon)
            self.img_thread.finished.connect(lambda t=self.img_thread: CardWidget._active_threads.discard(t))
            self.img_thread.start()
            
    def set_icon(self, data_bytes):
        try:
            if hasattr(self, 'icon_lbl') and self.icon_lbl:
                pixmap = QPixmap()
                pixmap.loadFromData(data_bytes)
                self.icon_lbl.setPixmap(pixmap.scaled(self.icon_lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception:
            pass

    def cleanup(self):
        th = getattr(self, 'img_thread', None)
        if th:
            self.img_thread = None
            try:
                th.loaded.disconnect(self.set_icon)
            except Exception:
                pass

    @classmethod
    def cleanup_all_threads(cls):
        for th in list(cls._active_threads):
            try:
                if th.isRunning():
                    th.quit()
                    th.wait(500)
                    if th.isRunning():
                        th.terminate()
                        th.wait(200)
            except Exception:
                pass
        cls._active_threads.clear()

    def mousePressEvent(self, event):
        self.clicked.emit(self.data)
        super().mousePressEvent(event)
