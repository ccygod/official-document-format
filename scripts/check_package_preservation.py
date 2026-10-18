#!/usr/bin/env python3
"""Check DOCX package preservation with an explicit allowlist of changed parts."""
from zipfile import ZipFile
import argparse,sys
ap=argparse.ArgumentParser(); ap.add_argument('baseline'); ap.add_argument('final'); ap.add_argument('--allow',action='append',default=[]); a=ap.parse_args()
with ZipFile(a.baseline) as x, ZipFile(a.final) as y:
 if x.namelist()!=y.namelist(): print('FAIL: package part list changed'); sys.exit(1)
 changed=[n for n in x.namelist() if x.read(n)!=y.read(n)]
 bad=[n for n in changed if n not in a.allow]
 print('changed_parts=',changed)
 if bad: print('FAIL: unexpected changes',bad); sys.exit(1)
 print('PASS: all changes are allowlisted')
