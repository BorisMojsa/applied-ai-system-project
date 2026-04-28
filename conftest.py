import sys
from pathlib import Path

# Allow `pytest` from repo root without requiring editable installs.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
