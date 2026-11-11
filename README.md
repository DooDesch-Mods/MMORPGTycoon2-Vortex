# MMORPG Tycoon 2 Vortex Extension

> 🛟 **Need help or found a bug?** Get support at [support.doodesch.de/vortex](https://support.doodesch.de/vortex).

Adds MMORPG Tycoon 2 to Vortex. Vortex finds the Steam installation and deploys with its own hardlink deployment. One installer places every archive:

| Archive contains | Installed to |
| --- | --- |
| `framework-package.json` (MT2 Mod Framework Runtime) | the game folder, plus a generated `mt2fw.json` that points the framework at `<game>\mt2fw-profile` |
| `mod.json` (framework mod) | `<game>\mt2fw-profile\mods\<id>\` |
| anything else (classic mod) | `<game>\mt2fw-profile\game-data\<SteamID64>\mod\<folder>\` |

All Vortex profiles share the one framework profile `<game>\mt2fw-profile`. Your worlds and settings are stored there in `game-data`.

Every install step and every failure is written to the Vortex log with the prefix `MT2:`.

## Install

1. Download `MMORPGTycoon2-Vortex-<version>.zip` from [Nexus](https://www.nexusmods.com/site/mods/2465) or the [GitHub releases](https://github.com/DooDesch-Mods/MMORPGTycoon2-Vortex/releases).
2. In Vortex **Extensions**, use **Drop File(s)** to install the ZIP, then restart Vortex.
3. Manage **MMORPG Tycoon 2**. The staging folder must be on the same drive as the game.
4. Install the **MT2 Mod Framework Runtime** ZIP, then your mod ZIPs. Enable them and deploy with the game closed.
5. Start the game through Steam. F10 opens the framework **Mods** menu.

The [Vortex guide](https://github.com/DooDesch-Mods/MMORPGTycoon2-ModFramework/blob/main/docs/guides/vortex.md) in the framework docs covers the full setup, updating from 0.1.x and removal.

## Classic mods

Classic mods are mods without a `mod.json`. They load only while the Framework Runtime is enabled and deployed, because the runtime points the game's data folder to `mt2fw-profile\game-data`. Without it, the extension logs a warning and shows a Vortex notification after installing or deploying a classic mod. If the runtime rejects a new game build, the game uses its normal AppData folder; classic mods and worlds in `mt2fw-profile\game-data` stay on disk but are not loaded.

- If the archive starts with a game data folder (`buildings`, `building_definitions`, `building_themes`, `icons`, `materials`, `scenery`, `wall_themes`), its content goes into a folder named after the archive.
- Otherwise each top-level folder is a mod folder. Loose files at the top, such as readmes, are skipped.
- The SteamID64 comes from the signed-in Steam user. With Steam closed, the extension uses the single account folder in `mt2fw-profile\game-data` or `%APPDATA%\VectorStorm\MMORPG Tycoon 2`. With none or several, the install fails; sign in to Steam and try again.

MT2 Mod Manager packages (`manifest.json`), character cards and tools are not recognized; the installer treats them as classic mods. Install those by hand.

## Remove

Disable the mods and purge in Vortex. Vortex removes the files it deployed. `<game>\mt2fw-profile\game-data` keeps your worlds and settings.

## Development

```powershell
node --test
python tools/release.py package
```

`package` writes `dist/` with the ZIP, `SHA256SUMS.txt` and the release notes. The ZIP holds `index.js`, `info.json`, `gameart.png`, `package.json`, `README.md` and `LICENSE` at its root. The version lives in `extension/info.json` only. Steam app ID: 486860. Nexus game ID: 4452.

Releases: set the version in `extension/info.json`, add a `## <version>` section to `CHANGELOG.md`, then push the tag `v<version>`. The Release workflow builds the ZIP, creates the GitHub release and uploads the file to Nexus.

## License

Original extension code is MIT. The real-game artwork `extension/gameart.png` keeps its own rights, recorded in `media.json`.
