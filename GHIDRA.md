# Ghidra installers

One-shot scripts to download the official [Ghidra](https://github.com/NationalSecurityAgency/ghidra) PUBLIC release, install JDK 21 when needed, and launch the GUI.

| Platform | Script | Install location |
|----------|--------|------------------|
| **Windows 10/11** | `install-ghidra.bat` or `install-ghidra.ps1` | `%LOCALAPPDATA%\Ghidra\` |
| **Ubuntu 26.04 / 24.04** | `install-ghidra.sh` | `~/.local/share/ghidra/` |

Installer version: **1.1.1**

## Windows

**Recommended** — double-click **`install-ghidra.bat`** (no execution-policy change needed).

Or from PowerShell:

```powershell
git pull origin main
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-ghidra.ps1
```

Running `.\install-ghidra.ps1` directly requires signing or `RemoteSigned` plus an unblock; the `.bat` wrapper always bypasses policy for this one script.

| Flag | Purpose |
|------|---------|
| `-InstallOnly` | Install without launching |
| `-RunOnly` | Launch an existing install |
| `-Version 12.1.2` | Pin a specific release |
| `-DesktopShortcut` | Also add a Desktop shortcut |
| `-Force` | Re-download and reinstall |

**Run Ghidra after install**

- Start Menu → **Ghidra**
- New terminal: `ghidra`
- Direct: `%LOCALAPPDATA%\Ghidra\current\ghidraRun.bat`

JDK 21 is installed via `winget` (Temurin, with Microsoft OpenJDK fallback) when not already present.

## Linux (Ubuntu)

```bash
git pull origin main
chmod +x install-ghidra.sh
./install-ghidra.sh
```

| Flag | Purpose |
|------|---------|
| `--install-only` | Install without launching |
| `--run-only` | Launch an existing install |
| `--version 12.1.2` | Pin a specific release |
| `--xvfb` | Launch under a virtual display (SSH/headless) |
| `--force` | Re-download and reinstall |

**Run Ghidra after install**

```bash
export PATH="$HOME/.local/bin:$PATH"
ghidra
```

Or: `~/.local/share/ghidra/current/ghidraRun`

### Ubuntu 26.04 apt note

Ghidra does **not** need Gradle. If `apt update` fails because of a stale PPA such as `ppa:cwchien/gradle`, the Linux script disables it automatically. To remove it manually:

```bash
sudo add-apt-repository --remove ppa:cwchien/gradle
sudo apt-get update
```

## Updating Ghidra

Re-run the installer for your platform. Without `-Force` / `--force`, an existing install is reused. Pass `-Force` or `--force` to fetch the latest release zip again.

## Requirements

- **JDK 21** (installed automatically if missing)
- **x86_64** CPU
- **~600 MB** disk for the download + extract
- Ghidra install path must **not** contain `!` (Java limitation)
