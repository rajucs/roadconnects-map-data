#!/usr/bin/env python3
"""Merges the *.meta.json files of this build into manifest.json. A country that was not rebuilt keeps its old entry (from the previous manifest)."""
import json
import os
import sys

countries = {c['code']: c for c in json.load(open('countries.json'))}
dist, old_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
manifest = {}
if os.path.exists(old_path):
    try:
        manifest = {c['code']: c for c in json.load(open(old_path)).get('countries', [])}
    except (ValueError, KeyError):
        manifest = {}
for f in sorted(os.listdir(dist)):
    if not f.endswith('.meta.json'):
        continue
    meta = json.load(open(os.path.join(dist, f)))
    c = countries[meta['code']]
    manifest[meta['code']] = {
        'code': c['code'], 'name': c['name'], 'tier': meta['tier'], 'places': meta['places'], 'bytes': meta['bytes'],
        'built': meta['built'], 'box': c['box'], 'file': c['code'] + '.ndjson.gz',
    }
ordered = [manifest[c] for c in countries if c in manifest]
json.dump({'license': 'ODbL 1.0, (c) OpenStreetMap contributors', 'countries': ordered}, open(out_path, 'w'), indent=1)
print(json.dumps(ordered, indent=1))
