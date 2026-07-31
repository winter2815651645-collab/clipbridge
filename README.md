# ClipBridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey)](https://www.microsoft.com/windows)
[![Release](https://img.shields.io/github/v/release/winter2815651645-collab/clipbridge)](https://github.com/winter2815651645-collab/clipbridge/releases)

Windows clipboard CJK encoding bridge. Fixes garbled Chinese/Japanese/Korean text when pasting into Chromium and Electron apps.

![screenshot](assets/screenshot.png)

## The problem

Copy Chinese text. Paste into VS Code, Discord, or Notion. Get `æŽ§åˆ¶` instead of `控制`.

This is not one app's bug. It is a **Chromium WebView clipboard encoding defect** that affects every Windows desktop app built on Chromium or Electron. The chain: some apps write UTF-8 bytes into `CF_UNICODETEXT` (which expects UTF-16LE), and the receiving WebView reads garbage.

## Apps known to trigger this

| Category | Examples |
|----------|----------|
| Code editors | Cursor, VS Code, Windsurf |
| Chat / collaboration | Discord, Slack, Teams |
| Notes / knowledge | Notion, Obsidian |
| AI / dev tools | GitHub Copilot Chat |
| Any Electron app | ...and anything else with a Chromium paste path |

Even if your current editor has patched this, other apps on your system may still trigger it.

## What ClipBridge does

Copy CJK text from anywhere. ClipBridge detects the corruption, recovers the original text, and writes it back to the clipboard. Paste works.

Two recovery patterns:

| Pattern | What happens | Recovery |
|---------|-------------|----------|
| **A** | UTF-8 bytes expanded into UTF-16LE with `0x00` alternation | Extract even bytes, decode as UTF-8 |
| **B** | Raw UTF-8 bytes stuffed into `CF_UNICODETEXT` | Decode as UTF-8 with alpha ratio guard (>50%) |

## Features

- **Auto monitor** — polls clipboard every 500ms, fixes encoding on the fly
- **Win+Shift+V** — manual hotkey to fix current clipboard content
- **System tray** — runs in background with context menu (pause, about, exit)
- **Popup window** — dark Slate theme, toggle auto-fix on/off
- **Zero dependencies** — Python 3 stdlib only (tkinter + ctypes)

## Installation

```bash
# Download clipbridge.pyw
# Run it (no console window):
pythonw clipbridge.pyw
```

To enable debug logging (writes clipboard activity to `bridge_debug.log` on your Desktop):

```bash
pythonw clipbridge.pyw --debug
```

### Auto-start on boot

1. Place `clipbridge-startup.vbs` **in the same folder** as `clipbridge.pyw`
2. Create a shortcut in your Startup folder:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```

The shortcut target should point to:

```
wscript.exe "C:\path\to\clipbridge-startup.vbs"
```

> **Note for non-English Windows users:** The VBS file contains only ASCII. If you create your own VBS wrapper, save it as **ANSI/ASCII**, not UTF-8. VBScript does not support UTF-8 and will fail with "Invalid character" errors on Chinese/Japanese/Korean Windows.

## Requirements

- Windows 10/11
- Python 3.10+

No pip install needed. Uses only tkinter and ctypes from the standard library.

## How it works

```
Any app (browser, WeChat, Notepad...)
    |  Ctrl+C
    v
Windows Clipboard (CF_UNICODETEXT)
    |  ClipBridge polls every 500ms
    v
Encoding detection (Pattern A vs Pattern B)
    |  Recovery
    v
Clipboard written back with correct UTF-16LE
    |  Ctrl+V
    v
Target app — Chinese displays correctly
```

## Tech stack

| Layer | Tech |
|-------|------|
| UI | tkinter (tray icon + popup) |
| Clipboard | Win32 API via ctypes (`OpenClipboard`, `GetClipboardData`, `SetClipboardData`) |
| Hotkey | `GetAsyncKeyState` polling |
| Tray icon | `Shell_NotifyIconW` + GDI custom drawing |
| Encoding | Pure Python byte-level recovery (`clipbridge_pure.py`) |

## Comparison

| | ClipBridge | Clipboard helpers | App-specific fixes |
|---|---|---|---|
| Scope | All Chromium/Electron apps | Any app | One app |
| Encoding fix | Pattern A + B recovery | Format conversion only | Depends on app |
| Dependencies | Zero (Python stdlib) | Varies | N/A |
| Runs in tray | Yes | Sometimes | No |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

## Author

James Wang
