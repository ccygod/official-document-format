#!/usr/bin/env python3
import argparse,json
from ooxml_model import OOXMLModel
ap=argparse.ArgumentParser(); ap.add_argument('first'); ap.add_argument('second'); a=ap.parse_args(); x=OOXMLModel(a.first).snapshot(); y=OOXMLModel(a.second).snapshot();
if x!=y:
 print('FAIL: semantic snapshots differ');
 for k in x:
  if x[k]!=y[k]: print('changed:',k)
 raise SystemExit(1)
print('PASS: semantic snapshots identical')
