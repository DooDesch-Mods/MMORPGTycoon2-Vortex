# MMORPG Tycoon 2 Vortex Extension

Vortex game extension for MMORPG Tycoon 2 (`extension/index.js`, plain CommonJS, no build step). It installs the MT2 Mod Framework Runtime, framework mods and classic mods through Vortex's own hardlink deployment. It reads nothing from the Framework repository.

## Commands

```powershell
node --test test/                  # extension tests
python tools/release.py package    # build dist/ (ZIP, SHA256SUMS.txt, notes)
```

## Rules

- The version lives in `extension/info.json` only. A release needs a matching `## <version>` section in `CHANGELOG.md`.
- A pushed tag `v<version>` runs `release.yml`: GitHub release, then Nexus upload. Do not push tags, create releases or upload to Nexus unless the owner says so.
- `listing/` holds the Nexus page text. It goes online by hand, never from CI.
- Log every caught error with `log(...)` from `vortex-api`; never swallow one.
- `README.md` keeps the support line at the top and ships inside the ZIP. Docs and repo text are English.
- Work locally unless the owner authorizes commits, pushes, releases or hosting.
