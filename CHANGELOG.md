# Changelog

## [2.0.0] - 2026-07-31

### Changed
- Project renamed from "Cursor Bridge" to "ClipBridge" — same fix, all Chromium/Electron apps
- Main application: `cursor_bridge.pyw` → `clipbridge.pyw`
- Startup script: `cursor-bridge-startup.vbs` → `clipbridge-startup.vbs`
- Encoding logic extracted to standalone `clipbridge_pure.py` (importable, testable without Windows)
- Version number bumped to v2.0.0 to reflect the repositioning

### Fixed
- Test file now correctly imports from `clipbridge_pure` instead of non-existent `cursor_bridge_pure`

## [1.9.0] - 2026-07-09

### Added
- Initial public release
- Auto clipboard monitor with 500ms polling
- Win+Shift+V global hotkey
- System tray icon with context menu (pause, about, exit)
- Popup window with dark Slate theme and toggle switch
- Pattern A recovery: byte-expanded UTF-8 in UTF-16LE (0x00 alternation)
- Pattern B recovery: raw UTF-8 bytes in CF_UNICODETEXT with alpha ratio guard (>50%)
- GDI custom tray icon (light blue bridge on dark background)
- Drag support on popup window via invisible title bar hit area
- Auto-start VBS script for boot launch
