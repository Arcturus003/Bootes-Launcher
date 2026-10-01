from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import minecraft_launcher_lib

CLIENT_ID = "00000000402b5328"
REDIRECT_URI = "https://login.live.com/oauth20_desktop.srf"

class MicrosoftLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Microsoft ile Giriş Yap")
        self.resize(500, 600)
        self.login_data = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        
        self.browser.urlChanged.connect(self.on_url_changed)
        
        login_url, self.state, self.code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(CLIENT_ID, REDIRECT_URI)
        self.browser.setUrl(QUrl(login_url))
        
    def on_url_changed(self, url: QUrl):
        url_str = url.toString()
        if minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url_str):
            auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(url_str, self.state)
            if auth_code:
                try:
                    self.login_data = minecraft_launcher_lib.microsoft_account.complete_login(CLIENT_ID, None, REDIRECT_URI, auth_code, self.code_verifier)
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Giriş tamamlanamadı:\n{str(e)}")
                    self.reject()
                    self.reject()
            else:
                QMessageBox.critical(self, "Hata", "Yetkilendirme kodu alınamadı.")
                self.reject()

    def get_account_data(self):
        return self.login_data
