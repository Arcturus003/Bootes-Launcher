# Vega Launcher E2E Test Suite Readiness (`TEST_READY.md`)

## 1. Test Command

The entire test suite can be run headlessly via any of the following commands from the project root:

```powershell
# Preferred runner (includes formatted summary report):
python tests/run_tests.py -v

# Filter by tier:
python tests/run_tests.py --tier 1
python tests/run_tests.py --tier 2
python tests/run_tests.py --tier 3
python tests/run_tests.py --tier 4

# Standard library unittest discovery:
python -m unittest discover -s tests -p "test_*.py"
```

All tests execute headlessly (`QT_QPA_PLATFORM=offscreen`) without opening visual windows or blocking background execution.

---

## 2. Test Coverage Checklist

### Tier 1: Feature Coverage (>= 5 test cases per feature)
- [x] **Application Startup (6 tests)**
  - `test_qapplication_offscreen_initialization` — Offscreen platform verification
  - `test_vega_launcher_instantiation_and_window_properties` — Title and dimensions (1200x720)
  - `test_vega_launcher_core_widgets_present` — NavBar, Stack, ProfilePage, ServerWidget, ActionBar, StatusBar
  - `test_vega_launcher_directory_initialization` — Auto-creation of `profiles/` and `launcher_config.json`
  - `test_vega_launcher_navigation_tabs` — Navigation between tabs and QStackedWidget page switching
  - `test_vega_launcher_filter_profiles` — Dynamic profile list filtering
- [x] **Profile Dialog Initialization (6 tests)**
  - `test_edit_profile_dialog_init` — Title, name input, and RAM spinbox configuration
  - `test_edit_profile_dialog_get_data` — Data extraction and whitespace stripping
  - `test_profile_select_dialog_empty_list` — OK button disabled when list is empty
  - `test_profile_select_dialog_with_items` — Dropdown population and OK button enabled
  - `test_profile_select_dialog_selection_methods` — Consistency of `get_selected()`, `selected_profile()`, `get_selected_profile()`
  - `test_add_profile_dialog_instantiation_contract` — AddProfileDialog instantiation contract
- [x] **Config Persistence (6 tests)**
  - `test_save_config_creates_valid_json` — JSON structure and file serialization
  - `test_save_config_persists_profiles` — Profile metadata persistence
  - `test_load_config_restores_profiles` — Deserialization of profiles from disk
  - `test_load_config_auto_discovers_unindexed_folders` — Auto-discovery of unindexed disk folders
  - `test_load_config_path_normalization` — Normalization of profile paths to local directory
  - `test_config_auth_session_persistence_contract` — Microsoft login session (`ms_login`) persistence
- [x] **Server File Pre-generation / Zero-Restart First Launch (5 tests)**
  - `test_default_server_properties_content` — Verification of `DEFAULT_SERVER_PROPERTIES` settings
  - `test_server_creation_pregenerates_eula_and_properties` — Pre-generation of `eula.txt` (`eula=true`) and `server.properties`
  - `test_ensure_server_files_fixes_false_eula` — Auto-correction of `eula=false` to `eula=true`
  - `test_ensure_server_files_appends_missing_eula` — Appending `eula=true` when missing
  - `test_server_properties_crud` — Reading, modifying, and saving `server.properties` via UI controls
- [x] **Playit IP Extraction (6 tests)**
  - `test_playit_ip_extraction_standard` — Extraction of `*.auto.playit.gg:PORT`
  - `test_playit_ip_extraction_ply_gg` — Extraction of `*.ply.gg:PORT`
  - `test_playit_bare_domain_ignored` — Bare `playit.gg` rejected as server address
  - `test_playit_claim_url_extraction` — Extraction of verification URLs (`/claim/` and `/mc/`)
  - `test_playit_download_and_non_playit_ignored` — Download links and regular logs filtered
  - `test_playit_ip_deduplication` — Prevention of redundant IP update emissions

### Tier 2: Boundary & Corner Cases (10 tests)
- [x] `test_empty_profile_name` — Handling empty profile name strings
- [x] `test_whitespace_profile_name` — Stripping whitespace-only names to empty string
- [x] `test_special_characters_in_profile_name` — Unicode and Turkish characters (`ç, ğ, ı, ö, ş, ü, İ`) in names and paths
- [x] `test_boundary_ram_clamping` — Clamping below minimum (1024 MB) and above maximum (32768 MB)
- [x] `test_corrupted_json_syntax` — Safe recovery from syntax-corrupted configuration files
- [x] `test_corrupted_json_non_dict_root` — Safe recovery from non-dict root JSON values
- [x] `test_corrupted_json_null_profiles` — Safe handling of null profiles fields
- [x] `test_missing_profiles_directory` — Auto-creation of missing profiles directory
- [x] `test_missing_config_file_creates_default` — Auto-generation of default config file with `profiles` and `ms_login`
- [x] `test_missing_server_properties_file` — Graceful handling of missing `server.properties`

### Tier 3: Cross-Feature Combinations (4 tests)
- [x] `test_profile_full_lifecycle` — Create -> Edit -> Save -> Reload -> Verify
- [x] `test_profile_to_server_import_flow` — Selection -> File pre-generation -> Mods & Config copy
- [x] `test_server_creation_and_properties_workflow` — Create server -> Modify settings -> Save -> Reload
- [x] `test_launch_options_and_mc_dir_contract` — Game launch options and `%APPDATA%/.minecraft` unification

### Tier 4: Real-World Scenarios (5 tests)
- [x] `test_headless_complete_gui_startup` — Full instantiation without fatal errors
- [x] `test_clean_shutdown_and_thread_lifecycle_contract` — Active thread shutdown and zombie prevention
- [x] `test_pyside6_signal_signatures_compliance` — Rule 2: No `finished = Signal(...)` argument override across all project QThreads
- [x] `test_pyside6_thread_ui_safety_signals` — Rule 1: Signal-based thread-to-UI communication
- [x] `test_server_thread_process_lifecycle` — Process PID tracking, command dispatch, and shutdown signals

---

## 3. Test Execution Results

| Test Suite | Total Tests | Passed | Failed | Status |
|---|---|---|---|---|
| Tier 1: Feature Coverage | 29 | 29 | 0 | **100% PASS** |
| Tier 2: Boundary & Corner Cases | 10 | 10 | 0 | **100% PASS** |
| Tier 3: Cross-Feature Workflows | 4 | 4 | 0 | **100% PASS** |
| Tier 4: Real-World Scenarios | 5 | 4 | 1 | **80% PASS** (1 Expected M2 Contract) |
| **Total** | **48** | **47** | **1** | **97.9% PASS** |

Execution Time: ~9.6 seconds.

---

## 4. Discovered Implementation Defects (For Escalation)

The following defect is actively tracked and asserted by the test suite:

### Defect 1: Missing Window `closeEvent` and Thread Teardown (Milestone M2 Feature 6)
- **Failing Test**: `tests.test_tier4_real_world.TestRealWorldScenarios.test_clean_shutdown_and_thread_lifecycle_contract`
- **Location**: `main.py:VegaLauncher`
- **Observation**: `VegaLauncher` does not implement `closeEvent`. Background threads in `self._active_threads` (e.g. `UpdateCheckerThread`) remain running when the application is closed. If Python process teardown commences while a QThread is executing in C++, PySide6 throws `QThread: Destroyed while thread is still running` and exits with error code 1.
- **Contract Requirement (`PROJECT.md` § Interface Contracts)**:
  `VegaLauncher.closeEvent(event)` must iterate over `self._active_threads`, call `th.quit()` and `th.wait()`, invoke `server_widget.cleanup()`, and accept the close event cleanly with exit code 0.
- **Assigned Milestone**: M2 (Thread Safety & Process Lifecycle).
