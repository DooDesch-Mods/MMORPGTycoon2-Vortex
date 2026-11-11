# Changelog

Versions follow the extension version in `extension/info.json`. Releases before 0.2.0 were published from the [MT2 Mod Framework repository](https://github.com/DooDesch-Mods/MMORPGTycoon2-ModFramework) as `vortex-v*` tags.

## 0.2.1

- The extension now lives in its own repository, [MMORPGTycoon2-Vortex](https://github.com/DooDesch-Mods/MMORPGTycoon2-Vortex). README and links are updated; the extension itself is unchanged from 0.2.0.

## 0.2.0

### Changed

- Deploy with Vortex's own hardlink deployment. The staging folder must be on the same drive as the game.
- Install the runtime and framework mods into one framework profile, `<game>\mt2fw-profile`, shared by all Vortex profiles.
- Install classic mods without `mod.json`, not only scenery packs. They need the player runtime.
- Write every install step and failure to the Vortex log.

### Removed

- Protected copy deployment, the game build check, ownership records and per-profile saves.

### Install

Purge in Vortex before installing 0.2.0, then install the extension ZIP, restart Vortex and deploy. The [Vortex guide](https://github.com/DooDesch-Mods/MMORPGTycoon2-ModFramework/blob/main/docs/guides/vortex.md) lists leftover files to delete and how to keep your worlds.

## 0.1.4

### Fixed

- Install mods when Vortex staging and the game are on different drives. No folder move is needed.
- Check and purge Vortex mods without getting blocked by an unrelated loader in the game folder.
- Back up the recognized old standalone Multiplayer loader before switching to Framework mods.

### Changed

- Protected deployment now copies files and keeps track of their checksums. Unknown or edited files stay protected.
- Keep your saves, mod settings and staging packages when disabling or removing mods.

### Install

Install the extension ZIP in Vortex's Extensions view, then restart Vortex and deploy. Keep your existing staging folder. Framework and Multiplayer downloads are unchanged.

## 0.1.3

### Fixed

- Recover from "No deployment method available" when the staging folder is on a different drive from the game.
- Move past first-time setup with an empty profile while preserving any loader already in the game folder.

### Changed

- Show the staging and game drives with clear instructions for choosing the staging folder.
- Explain how to resolve an existing loader conflict before deploying.

### Install

Install the extension ZIP from Vortex's Extensions view and restart Vortex. In Settings > Mods, keep the Mod Staging Folder on the same drive as the game, outside the game folder. Framework and Multiplayer downloads are unchanged.

## 0.1.1

- Install original model-only classic scenery ZIPs, including More Sceneries - Lite Mode 1.3.
- Preserve original model bytes and scope deployment to the selected Vortex profile and Steam account.
- Validate model headers, staged inventories and competing virtual resources before deployment.
- Detect scenery type before activation and keep scenery folders out of the framework mod list.
- Retain the exact deployment and native model-loading acceptance limits (`evidence/vortex-scenery-acceptance.json` in the framework repository history).
