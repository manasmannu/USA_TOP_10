import sqlite3, requests, os, shutil, time
from pathlib import Path

DESTINATIONS = [
    "New York City, New York",
    "San Francisco, California",
    "Miami, Florida",
    "Grand Canyon National Park, Arizona",
    "Yellowstone National Park, Wyoming",
    "Honolulu, Hawaii",
    "New Orleans, Louisiana",
    "Chicago, Illinois",
    "Washington, D.C.",
    "Las Vegas, Nevada",
]

DEFAULTS = {
    "New York City, New York":      ("city,food,art", "Apr-Jun, Sep-Oct"),
    "San Francisco, California":    ("city,coast,scenic", "May-Oct"),
    "Miami, Florida":               ("beach,nightlife", "Dec-Apr"),
    "Grand Canyon National Park, Arizona": ("nature,hiking,park", "Mar-May, Sep-Nov"),
    "Yellowstone National Park, Wyoming":  ("nature,park,wildlife", "Jun-Sep"),
    "Honolulu, Hawaii":             ("beach,tropical", "Apr-Oct"),
    "New Orleans, Louisiana":       ("music,food,history", "Feb-May, Oct-Nov"),
    "Chicago, Illinois":            ("city,art,food", "May-Oct"),
    "Washington, D.C.":             ("history,museums,city", "Mar-Jun, Sep-Oct"),
    "Las Vegas, Nevada":            ("nightlife,entertainment,desert", "Mar-May, Sep-Nov"),
}

# --- Wikipedia API endpoints
WIKI_SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
WIKI_QUERY_API   = "https://en.wikipedia.org/w/api.php"

# *** IMPORTANT: identify your script per Wikipedia API etiquette ***
HEADERS = {
    "User-Agent": f"usa-top10-seeder/1.0 ({os.getenv('CONTACT_EMAIL', 'anonymous@example.com')}) Python requests"
}

# Where to drop downloaded thumbs (adjust if your Angular path is different)
IMG_DIR = Path("../frontend-angular/usa-top10/src/assets/images")

def http_get(url, params=None, stream=False):
    """GET with headers + simple retry on 429/5xx."""
    for i in range(4):
        r = requests.get(url, params=params, headers=HEADERS, timeout=20, stream=stream)
        # Retry on 429 or 5xx
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(1.5 * (i + 1))
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()

def wiki_title_for(query: str) -> str | None:
    """Use the modern search API to get the best title for a query."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 1,
        "format": "json"
    }
    r = http_get(WIKI_QUERY_API, params=params)
    js = r.json()
    hits = js.get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None

def wiki_summary(title: str) -> dict | None:
    """Get summary + thumbnail + coordinates for a known title."""
    r = http_get(WIKI_SUMMARY_API + requests.utils.quote(title))
    js = r.json()
    out = {
        "title": js.get("title"),
        "summary": js.get("extract", ""),
        "lat": None, "lon": None,
        "thumb": None
    }
    thumb = js.get("thumbnail", {})
    if thumb and thumb.get("source"):
        out["thumb"] = thumb["source"]
    if js.get("coordinates"):
        out["lat"] = js["coordinates"].get("lat")
        out["lon"] = js["coordinates"].get("lon")
    return out

def download_image(url: str, out_name: str):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    r = http_get(url, stream=True)
    with open(IMG_DIR / out_name, "wb") as f:
        shutil.copyfileobj(r.raw, f)

def to_hero_filename(name: str) -> str:
    base = name.split(",")[0].lower().replace(" ", "")
    return f"{base}.jpg"

def guess_region(state: str) -> str:
    if state in ("California", "Arizona", "Nevada", "Wyoming"): return "West"
    if state in ("New York", "D.C."): return "Northeast"
    if state in ("Florida", "Louisiana"): return "Southeast"
    if state in ("Hawaii",): return "Pacific"
    if state in ("Illinois",): return "Midwest"
    return "USA"

def main():
    rows = []
    for i, place in enumerate(DESTINATIONS, start=1):
        title = wiki_title_for(place) or place
        info = wiki_summary(title) or {}
        short = (info.get("summary") or "").strip().split("\n")[0]
        short = (short[:220].rstrip() + "…") if len(short) > 220 else short
        lat, lon = info.get("lat"), info.get("lon")
        tags, best = DEFAULTS.get(place, ("city", "All year"))
        hero = to_hero_filename(place)

        # Try image
        if info.get("thumb"):
            try: download_image(info["thumb"], hero)
            except Exception: pass

        if "," in place:
            city, state = [x.strip() for x in place.split(",", 1)]
        else:
            city, state = place, ""

        region = guess_region(state)
        rows.append((i, city, state, region, lat, lon, short, best, tags, hero))

    # Build seed.sql
    seed_sql = [
        "DROP TABLE IF EXISTS destinations;",
        "CREATE TABLE destinations (id INTEGER PRIMARY KEY, name TEXT, state TEXT, region TEXT, lat REAL, lon REAL, short_desc TEXT, best_months TEXT, tags TEXT, hero_image TEXT);"
    ]
    for r in rows:
        id_, name, state, region, lat, lon, short, best, tags, hero = r
        esc = lambda s: (s or "").replace("'", "''")
        seed_sql.append(
            f"INSERT INTO destinations (id,name,state,region,lat,lon,short_desc,best_months,tags,hero_image) VALUES "
            f"({id_},'{esc(name)}','{esc(state)}','{esc(region)}',{lat if lat is not None else 'NULL'},{lon if lon is not None else 'NULL'},'{esc(short)}','{esc(best)}','{esc(tags)}','{esc(hero)}');"
        )

    Path("seed.sql").write_text("\n".join(seed_sql), encoding="utf-8")
    print("Wrote backend-python/seed.sql")

    # Write db.sqlite3 too
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    cur.executescript("\n".join(seed_sql))
    con.commit(); con.close()
    print("Wrote backend-python/db.sqlite3")

if __name__ == "__main__":
    main()