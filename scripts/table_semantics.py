"""Deterministic table-cell role classification shared by writer and checker."""
import re

_SENTENCE = re.compile(r'[，。；：]')

def is_prose_cell(text: str) -> bool:
    """Return True for wrapped explanatory prose, False for compact fields."""
    text = (text or '').strip()
    return (len(text) >= 12 and bool(_SENTENCE.search(text))) or (len(text) >= 20 and '、' in text)

def cell_style_id(text: str, header: bool = False) -> str:
    return '32' if (not header and is_prose_cell(text)) else '31'
