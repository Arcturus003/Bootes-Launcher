import hashlib
import json
import os

FILES_TO_CHECK = [
    "main.py",
    "server_widget.py",
    "card_widget.py",
    "mod_manager.py",
    "engine_installer.py",
    "playtime_tracker.py",
    "vanilla_thread.py",
    "auth_window.py",
    "server_thread.py",
    "ui_components.py",
    "server_downloader.py",
    "shortcut_creator.py"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTEGRITY_FILE = os.path.join(BASE_DIR, ".integrity")
def calculate_file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_hashes():
    hashes = {}
    for filename in FILES_TO_CHECK:
        abs_path = os.path.join(BASE_DIR, filename)
        file_hash = calculate_file_hash(abs_path)
        if file_hash:
            hashes[filename] = file_hash
    with open(INTEGRITY_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=4)
    print(f"Hashes generated and saved to {INTEGRITY_FILE}")

def verify_integrity():
    import sys
    if getattr(sys, 'frozen', False):
        # When running as a compiled .exe (PyInstaller/Nuitka), the raw .py files 
        # do not exist to be hashed. The code is already packed inside the executable.
        return True, []
        
    if not os.path.exists(INTEGRITY_FILE):
        return False, ["<missing_integrity_file>"]
    
    try:
        with open(INTEGRITY_FILE, "r", encoding="utf-8") as f:
            expected_hashes = json.load(f)
    except Exception:
        return False, ["<invalid_integrity_file>"]
        
    tampered_files = []
    for filename in FILES_TO_CHECK:
        if filename in expected_hashes:
            abs_path = os.path.join(BASE_DIR, filename)
            current_hash = calculate_file_hash(abs_path)
            if current_hash != expected_hashes[filename]:
                tampered_files.append(filename)
    
    if tampered_files:
        return False, tampered_files
    return True, []

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        generate_hashes()
    else:
        is_ok, tampered = verify_integrity()
        if is_ok:
            print("Integrity check passed.")
        else:
            print(f"Integrity check failed. Tampered files: {tampered}")
