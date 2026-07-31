# Contributing to ClipBridge

## Setup

```bash
git clone https://github.com/winter2815651645-collab/clipbridge.git
cd clipbridge
```

Python 3.10+ required. No pip install — stdlib only.

## Project structure

```
clipbridge/
├── clipbridge.pyw            # Main application (system tray + Win32 clipboard)
├── clipbridge_pure.py        # Encoding recovery logic (importable, testable)
├── tests/
│   └── test_clipbridge_pure.py
├── .github/workflows/
│   └── test.yml              # CI
└── clipbridge-startup.vbs    # Auto-start helper
```

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

## Coding conventions

- PEP 8
- English comments preferred for new code
- Pure logic goes in `clipbridge_pure.py` (testable without Windows)
- Win32 API code stays in `clipbridge.pyw`

## Pull requests

1. Fork and create a feature branch
2. Add tests for new behavior
3. Run `pytest` before submitting
4. Keep changes focused — one thing per PR

## Reporting bugs

Use the [bug report template](https://github.com/winter2815651645-collab/clipbridge/issues/new?template=bug_report.md). Include:
- Windows version
- Python version
- Target app and version
- Steps to reproduce
- Expected vs actual behavior

## Feature requests

Use the [feature request template](https://github.com/winter2815651645-collab/clipbridge/issues/new?template=feature_request.md). Explain the use case first.
