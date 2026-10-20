# Road Connects map data

Per-country files of the places Road Connects shows on its maps ("around here", fuel / food / hospitals along a route, hotels):
fuel stations, restaurants, hospitals, banks and ATMs, mosques and temples, schools, hotels, sights, shops, toilets, charging stations and toll plazas.

The files are cut from the free [Geofabrik](https://download.geofabrik.de) country extracts of [OpenStreetMap](https://www.openstreetmap.org)
by `tools/osm_pois.py`, every month, by the workflow in `.github/workflows/build.yml`.

| Where | What |
| --- | --- |
| Release `data` | `<code>.ndjson.gz` per country and `manifest.json` (countries, tier, number of places, size, build date, bounding box) |
| `countries.json` | which countries are built, their Geofabrik path, tier and rough bounding box |

**Tiers.** `full` is everything above; `lite` keeps only what a traveller needs on the road (fuel, food, hospitals and clinics, ATMs, toilets, charging, stays, sights, toll), about a third of the size. Big countries use `lite`.

**Line format.** One place per line: `["n123", lat, lng, {"amenity": "fuel", "name": "..."}]` (`n` node, `w` way, a way's point is the middle of its box).

**Add a country.** Add a row to `countries.json` (Geofabrik path from download.geofabrik.de) and run the workflow with `only` = the new code.

## Licence

The data is © OpenStreetMap contributors and available under the [Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Anyone using these files must credit "© OpenStreetMap contributors" and share any improved copy of the database under the same licence.
The scripts in `tools/` are MIT licensed.
