from PySide6.QtCore import QThread, Signal
import time

class PlaytimeTrackerThread(QThread):
    tracking_finished = Signal(str, int) # pid, elapsed_seconds
    
    def __init__(self, process, pid):
        super().__init__()
        self.process = process
        self.pid = pid
        self._is_running = True
        
    def stop(self):
        self._is_running = False

    def run(self):
        start_time = time.time()
        while self._is_running:
            if self.process is None:
                break
            try:
                if self.process.poll() is not None:
                    break
            except Exception:
                break
            time.sleep(0.5)
        end_time = time.time()
        
        elapsed = int(end_time - start_time)
        self.tracking_finished.emit(self.pid, elapsed)
