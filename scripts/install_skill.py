#!/usr/bin/env python3
"""Install this skill without overwriting an existing installation."""
import argparse
from pathlib import Path
import shutil

def install(source, destination):
    source=Path(source).resolve(); destination=Path(destination).expanduser().resolve()
    if destination.exists():
        raise FileExistsError(f"Destination exists: {destination}. Compare and back up your changes before updating.")
    if source == destination or source in destination.parents:
        raise ValueError("Destination must be outside the source repository.")
    if not (source/'SKILL.md').is_file():
        raise FileNotFoundError("Source is not a skill repository")
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source,destination,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','.DS_Store','.venv','.qa','dist','build'))
    return destination

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host',choices=['codex','claude'],default='codex')
    p.add_argument('--dest',type=Path,help='Explicit skill directory, including the skill name')
    a=p.parse_args();source=Path(__file__).resolve().parents[1]
    destination=a.dest or Path.home()/('.codex' if a.host=='codex' else '.claude')/'skills'/source.name
    try: print(f"Installed: {install(source,destination)}")
    except (OSError,ValueError) as e:p.exit(1,f"ERROR: {e}\n")
if __name__=='__main__':main()
