"""One versioned policy shared by CLI defaults and validation."""
import json
from pathlib import Path
POLICY=json.loads((Path(__file__).resolve().parents[1]/'config/official.json').read_text())
