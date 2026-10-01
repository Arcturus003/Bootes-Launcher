from PySide6.QtCore import QThread, Signal
import minecraft_launcher_lib

class DownloadVanillaThread(QThread):
    task_finished = Signal(bool, str)
    progress_update = Signal(str)
    progress_val = Signal(int)
    
    def __init__(self, version_id, minecraft_dir):
        super().__init__()
        self.version_id = version_id
        self.minecraft_dir = minecraft_dir
        self._max_val = 0
        
    def _set_max(self, max_val):
        self._max_val = max_val if max_val and max_val > 0 else 0
        
    def _set_progress(self, progress):
        normalized = int((progress / self._max_val) * 100) if self._max_val > 0 else progress
        self.progress_val.emit(min(100, max(0, normalized)))
        
    def run(self):
        callback = {
            "setStatus": lambda status: self.progress_update.emit(status),
            "setProgress": self._set_progress,
            "setMax": self._set_max
        }
        try:
            minecraft_launcher_lib.install.install_minecraft_version(self.version_id, self.minecraft_dir, callback=callback)
            self.task_finished.emit(True, "Kurulum başarılı.")
        except Exception as e:
            self.task_finished.emit(False, str(e))
