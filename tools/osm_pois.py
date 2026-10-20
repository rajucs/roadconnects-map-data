#!/usr/bin/env python3
"""
Cuts the places Road Connects shows ("around here", places along a route, hotels) out of an OpenStreetMap country extract
into <out>/<code>.ndjson.gz, one place per line: [osm_id, lat, lng, {tags}], and writes <out>/<code>.meta.json.

    python3 tools/osm_pois.py bangladesh.osm.pbf bd --tier full --out dist
    python3 tools/osm_pois.py india.osm.pbf in --tier lite --out dist

tier full: fuel, food, health, banks / ATMs, worship, schools, stays, sights, shops, toilets, charging, toll.
tier lite: only what a traveller needs on the road (fuel, food, hospitals / clinics, ATMs, toilets, charging, stays, sights, toll).

Points are nodes and ways (a way's point is the middle of its box, like Overpass "out center"). Relations are skipped.
Data: OpenStreetMap contributors, ODbL 1.0. See README.md.
"""
import argparse
import gzip
import json
import os
import sys
from datetime import date

import osmium

FULL = {
    'amenity': {'fuel', 'restaurant', 'cafe', 'fast_food', 'food_court', 'hospital', 'clinic', 'pharmacy', 'doctors', 'dentist', 'atm', 'bank',
                'place_of_worship', 'marketplace', 'school', 'college', 'university', 'toilets', 'charging_station'},
    'tourism': {'hotel', 'guest_house', 'hostel', 'motel', 'resort', 'apartment', 'attraction', 'museum', 'viewpoint', 'gallery', 'zoo', 'theme_park', 'chalet', 'camp_site'},
    'leisure': {'park', 'garden', 'nature_reserve'},
    'shop': {'supermarket', 'mall', 'department_store', 'convenience', 'marketplace'},
    'historic': True,
}
LITE = {
    'amenity': {'fuel', 'restaurant', 'cafe', 'fast_food', 'hospital', 'clinic', 'atm', 'toilets', 'charging_station'},
    'tourism': {'hotel', 'guest_house', 'hostel', 'motel', 'resort', 'attraction', 'museum', 'viewpoint', 'zoo', 'theme_park', 'camp_site'},
    'leisure': {'nature_reserve'},
    'shop': set(),
    'historic': True,
}
HIGHWAY = {'rest_area', 'services'}

KEEP = {
    'name', 'name:en', 'brand', 'operator', 'amenity', 'tourism', 'historic', 'leisure', 'shop', 'religion', 'denomination', 'cuisine',
    'opening_hours', 'phone', 'website', 'highway', 'barrier', 'toilets', 'capacity',
    'stars', 'rooms', 'contact:phone', 'contact:website',
}
KEEP_PREFIX = ('fuel:', 'socket:')


def wanted(t, kinds):
    a = t.get('amenity')
    if a in kinds['amenity']:
        return not (a == 'toilets' and t.get('access') == 'private')
    if t.get('tourism') in kinds['tourism']:
        return True
    if kinds['historic'] and t.get('historic', 'no') != 'no':
        return True
    if t.get('leisure') in kinds['leisure']:
        return True
    if t.get('shop') in kinds['shop']:
        return True
    if t.get('highway') in HIGHWAY:
        return True
    return t.get('barrier') == 'toll_booth'


def slim(tags):
    out = {}
    for k, v in tags:
        if k in KEEP or k.startswith(KEEP_PREFIX):
            out[k] = v[:300]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pbf')
    ap.add_argument('code', help='short name of the file, e.g. bd')
    ap.add_argument('--tier', choices=['full', 'lite'], default='full')
    ap.add_argument('--out', default='dist')
    a = ap.parse_args()
    kinds = FULL if a.tier == 'full' else LITE
    os.makedirs(a.out, exist_ok=True)
    dest = os.path.join(a.out, a.code + '.ndjson.gz')
    n = 0
    south, west, north, east = 90.0, 180.0, -90.0, -180.0
    with gzip.open(dest, 'wt', encoding='utf-8', compresslevel=9) as out:
        fp = osmium.FileProcessor(a.pbf).with_locations().with_filter(
            osmium.filter.KeyFilter('amenity', 'tourism', 'historic', 'leisure', 'shop', 'highway', 'barrier'))
        for o in fp:
            if not (o.is_node() or o.is_way()):
                continue
            tags = {k: v for k, v in o.tags}
            if not wanted(tags, kinds):
                continue
            if o.is_node():
                if not o.location.valid():
                    continue
                lat, lng, kind = o.location.lat, o.location.lon, 'n'
            else:
                pts = [(p.lat, p.lon) for p in o.nodes if p.location.valid()]
                if not pts:
                    continue
                lat = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
                lng = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
                kind = 'w'
            south, north = min(south, lat), max(north, lat)
            west, east = min(west, lng), max(east, lng)
            out.write(json.dumps([kind + str(o.id), round(lat, 6), round(lng, 6), slim(o.tags)], ensure_ascii=False, separators=(',', ':')) + '\n')
            n += 1
    meta = {'code': a.code, 'tier': a.tier, 'places': n, 'bytes': os.path.getsize(dest), 'built': date.today().isoformat(),
            'seen_box': [round(south, 2), round(west, 2), round(north, 2), round(east, 2)]}
    with open(os.path.join(a.out, a.code + '.meta.json'), 'w') as f:
        json.dump(meta, f)
    print('%s: %d places, %.1f MB' % (a.code, n, meta['bytes'] / 1e6))


if __name__ == '__main__':
    sys.exit(main())
