# Vega Launcher Test Infrastructure Documentation (`TEST_INFRA.md`)

## 1. Overview & Architecture

The Vega Launcher E2E test infrastructure is designed for **opaque-box, requirement-driven, headless verification** of the PySide6 Minecraft Launcher and Dedicated Server Manager.

Key architectural pillars:
- **Headless Offscreen Qt Platform**: All tests enforce `os.environ["QT_QPA_PLATFORM"] = "offscreen"` prior to loading PySide6 GUI components. This allows widget instantiation, event loops, layout engines, and styling without spawning physical desktop windows or blocking CI/CD runners.
- **Resource Isolation & Independence**: Every test extends `tests.test_base.BaseTestCase`, which allocates a unique temporary directory (`tempfile.mkdtemp`) for configuration, client profiles, and server folders. Real project assets, user credentials, and active server files are never mutated.
- **Strict Thread & Process Lifecycle Cleanup**: In compliance with PySide6 threading guidelines, `safe_cleanup_client()` and `BaseTestCase.tearDown()` inspect and stop any background threads (`_active_threads`, `_api_threads`) via `quit()` and `wait()`, preventing `QThread: Destroyed while thread is still running` fatal crashes and zombie worker processes.
- **Zero External Test Dependencies**: Built entirely upon Python's standard library `unittest` and `PySide6`. Does not require third-party test runners to be installed, yet fully compatible with `pytest` via `tests/conftest.py`.

---

## 2. Directory Layout & Modules

```
tests/
├── __init__.py                     # Test package initializer
├── run_tests.py                    # Standalone CLI test runner with tier filtering & summary report
├── conftest.py                     # Headless Qt session fixture for pytest interoperability
├── test_base.py                    # BaseTestCase, offscreen QApplication singleton, fixture helpers
├── test_tier1_features.py          # Tier 1: 5 Core Features (>=5 tests per feature, 29 tests total)
├── test_tier2_boundaries.py        # Tier 2: Boundary & Corner Cases (10 tests)
├── test_tier3_cross_features.py    # Tier 3: Cross-Feature Multi-Step Workflows (4 tests)
└── test_tier4_real_world.py        # Tier 4: Real-World Scenarios & PySide6 Compliance (5 tests)
```

---

## 3. Test Tiers & Coverage Mapping

### Tier 1: Feature Coverage (29 Tests)
Each core feature has at least 5 dedicated test cases:
1. **Application Startup (6 tests)**:
   - `test_qapplication_offscreen_initialization`: Offscreen headless Qt platform validation.
   - `test_vega_launcher_instantiation_and_window_properties`: Window title, dimensions (1200x720).
   - `test_vega_launcher_core_widgets_present`: Presence of NavBar, QStackedWidget, profile page, server page, ActionBar, statusBar.
   - `test_vega_launcher_directory_initialization`: Creation of `profiles/` and default configuration if absent.
   - `test_vega_launcher_navigation_tabs`: Switching between tabs ("home", "packs", "mods", "shaders", "bedrock_home", "dungeons_home", "server").
   - `test_vega_launcher_filter_profiles`: Real-time QListWidget filtering on profile search input.

2. **Profile Dialog Initialization (6 tests)**:
   - `test_edit_profile_dialog_init`: Verification of EditProfileDialog labels and initial values.
   - `test_edit_profile_dialog_get_data`: Stripped string name and integer RAM tuple return.
   - `test_profile_select_dialog_empty_list`: OK button disabled when profile list is empty.
   - `test_profile_select_dialog_with_items`: Dropdown population and OK button enabled.
   - `test_profile_select_dialog_selection_methods`: Verification of `get_selected()`, `selected_profile()`, and `get_selected_profile()`.
   - `test_add_profile_dialog_instantiation_contract`: AddProfileDialog instantiation contract without `AttributeError` (verifies M1 Feature 1 fix).

3. **Config Persistence (6 tests)**:
   - `test_save_config_creates_valid_json`: Valid JSON formatting and disk write verification.
   - `test_save_config_persists_profiles`: Persistence of profile properties (RAM, version, project_id, source).
   - `test_load_config_restores_profiles`: Deserialization of saved profiles into `client.profiles`.
   - `test_load_config_auto_discovers_unindexed_folders`: Disk folder auto-indexing with defaults (1.20.1, 4096 RAM).
   - `test_load_config_path_normalization`: Re-binding profile paths to current launcher profiles directory.
   - `test_config_auth_session_persistence_contract`: Verification of `ms_login` authentication session persistence (verifies M1 Feature 3).

4. **Server File Pre-generation / Zero-Restart First Launch (5 tests)**:
   - `test_default_server_properties_content`: Validation of `DEFAULT_SERVER_PROPERTIES` settings (`server-port=25565`, `online-mode=true`, `motd`, `difficulty`, `max-tick-time=-1`).
   - `test_server_creation_pregenerates_eula_and_properties`: Pre-generation of `eula.txt` (`eula=true`) and `server.properties` upon server creation.
   - `test_ensure_server_files_fixes_false_eula`: Automatic correction of `eula=false` to `eula=true` prior to launch.
   - `test_ensure_server_files_appends_missing_eula`: Appending `eula=true` if file exists but lacks consent statement.
   - `test_server_properties_crud`: UI control synchronization and persistence via `load_server_properties` and `save_server_properties`.

5. **Playit IP Extraction (6 tests)**:
   - `test_playit_ip_extraction_standard`: Extraction of `*.auto.playit.gg:PORT` from console stream.
   - `test_playit_ip_extraction_ply_gg`: Extraction of `*.ply.gg:PORT` domain format.
   - `test_playit_bare_domain_ignored`: Rejection of bare `playit.gg` domain without subdomain/port.
   - `test_playit_claim_url_extraction`: Detection of verification URLs (`https://playit.gg/claim/...` or `/mc/...`).
   - `test_playit_download_and_non_playit_ignored`: Filtering out download links and normal server log messages.
   - `test_playit_ip_deduplication`: Suppression of duplicate IP notifications when line repeats.

---

### Tier 2: Boundary & Corner Cases (10 Tests)
- `test_empty_profile_name`: Clean handling of empty profile names.
- `test_whitespace_profile_name`: Stripping leading/trailing/tab/newline whitespace.
- `test_special_characters_in_profile_name`: Support for Turkish characters (`ş, ç, ö, ğ, ü, ı, İ`), punctuation, hyphens, brackets, and Unicode in configs and filesystem paths.
- `test_boundary_ram_clamping`: Validation of QSpinBox min (1024 MB), max (32768 MB), and step clamping.
- `test_corrupted_json_syntax`: Graceful recovery from malformed JSON syntax in `launcher_config.json`.
- `test_corrupted_json_non_dict_root`: Handling invalid root JSON types (lists, integers, strings).
- `test_corrupted_json_null_profiles`: Handling `null` or missing profile keys.
- `test_missing_profiles_directory`: Re-creation of deleted `profiles/` directory on launch.
- `test_missing_config_file_creates_default`: Auto-generation of default config file with `profiles` and `ms_login`.
- `test_missing_server_properties_file`: Safe fallback in `load_server_properties()` when `server.properties` is absent.

---

### Tier 3: Cross-Feature Combinations (4 Tests)
- `test_profile_full_lifecycle`: Multi-step flow: Add profile -> Edit profile -> Save config -> Reload launcher from disk -> Verify state.
- `test_profile_to_server_import_flow`: Selection via ProfileSelectDialog -> Copying `mods/` and `config/` -> Pre-generating server files -> Verifying server directory integrity.
- `test_server_creation_and_properties_workflow`: Creating server -> Verifying pre-generated files -> Modifying settings via UI controls -> Saving properties -> Reloading and asserting persistence.
- `test_launch_options_and_mc_dir_contract`: Verification of game launch dictionary parameters and unification of Minecraft directory path with `self.mc_dir` (%APPDATA%/.minecraft).

---

### Tier 4: Real-World Scenarios & Concurrency Safety (5 Tests)
- `test_headless_complete_gui_startup`: Full instantiation of `VegaLauncher` without fatal errors or missing components.
- `test_clean_shutdown_and_thread_lifecycle_contract`: Verification that window close terminates background threads in `_active_threads` to prevent crashes on application exit (M2 Feature 6).
- `test_pyside6_signal_signatures_compliance`: Comprehensive inspection of all `QThread` subclasses across the codebase, enforcing PySide6 Rule 2 (no `finished = Signal(...)` with arguments).
- `test_pyside6_thread_ui_safety_signals`: Inspection of worker thread communication patterns, ensuring UI updates occur exclusively via PySide6 Signals.
- `test_server_thread_process_lifecycle`: Verification of `MinecraftServerThread` PID tracking (`get_pid()`), running flag lifecycle, safe command dispatch, and graceful shutdown signal handling.

---

## 4. How to Run the Tests

### Option A: Standard Test Runner (Recommended)
```powershell
# Run the entire test suite across all 4 tiers
python tests/run_tests.py

# Run a specific tier
python tests/run_tests.py --tier 1
python tests/run_tests.py --tier 2
python tests/run_tests.py --tier 3
python tests/run_tests.py --tier 4

# Run with verbose test-by-test output
python tests/run_tests.py -v
```

### Option B: Standard Python Unittest Discovery
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### Option C: Pytest (if installed)
```powershell
pytest tests/ -v
```
