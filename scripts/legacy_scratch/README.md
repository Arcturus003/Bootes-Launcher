# Legacy Scratch Scripts Archive

This directory contains standalone exploratory, prototyping, and ad-hoc testing scripts developed during early phases of the project (e.g. testing Modrinth API, CurseForge endpoints, dependency resolution, and version downgrading).

These scripts are kept here for historical reference and documentation. They are not part of the core Nexus Client application or automated test suites.

## Relocated Files (21 files)
- `downgrade.py`: Prototype for testing Modrinth version downgrade fetching.
- `find_api.py`: Queries Modrinth API endpoints.
- `get_great_sage.py`: Prototype script downloading Great Sage modpack version data.
- `get_great_sage_all.py`: Prototype fetching all versions for Great Sage modpack.
- `get_tensura.py`: Downloads Tensura mod metadata from Modrinth.
- `install_prism.py`: Experimental script for downloading and extracting Prism Launcher standalone build.
- `modrinth_api.py`: Early prototype wrapper for Modrinth API (superseded by `mod_manager.py`).
- `modrinth_greatsage.py`: Modrinth search query test for Great Sage.
- `modrinth_other_modpacks.py`: Prototype testing Modrinth search with various modpack queries.
- `modrinth_slimes.py`: Slimes Adventure modpack dependency resolution testing.
- `modrinth_slimes_loaders.py`: Loader compatibility test for Slimes modpack.
- `modrinth_tensura_loaders.py`: Loader compatibility test for Tensura mod.
- `search_ablaze.py`: Modrinth search test for Ablaze mod.
- `search_deps.py`: Early prototype testing recursive Modrinth dependency tree resolution.
- `search_great_sage.py`: Modrinth search query filtering test for Great Sage.
- `search_modpacks.py`: Prototype querying modpacks on Modrinth API.
- `search_mods.py`: Prototype testing mod searching and facet filtering on Modrinth.
- `search_ui.py`: Prototype testing search query parameters for UI mods.
- `tensura_versions.py`: Modrinth version dumper for Tensura mod.
- `test_cf.py`: Ad-hoc test of CurseForge ForgeSvc API endpoint.
- `test_modrinth.py`: Ad-hoc test of Modrinth search API endpoint.
