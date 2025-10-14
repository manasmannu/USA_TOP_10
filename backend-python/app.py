from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

# Import the Wikipedia seeder
from generate_seed_from_wikipedia import main as regenerate_data

app = FastAPI(title="USA Top 10 Vacation Destinations")

# Enable CORS for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "db.sqlite3"

# Automatically refresh data when server starts
def refresh_data_on_start():
    print("[startup] Regenerating data from Wikipedia...")
    regenerate_data()
    print("[startup] Data regenerated successfully!")

refresh_data_on_start()

# ---------- ROUTES ----------

@app.get("/")
def home():
    return {"message": "Welcome to USA Top 10 Vacation Destinations API!"}

@app.get("/destinations")
def get_destinations():
    """Return all destinations from db."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row 
    cur = con.cursor()
    rows = cur.execute("SELECT * FROM destinations;").fetchall()
    con.close()
    items = [dict(r) for r in rows]              # <-- list of dicts
    return {"destinations": items}  

# @app.get("/destinations")
# def get_destinations():
#     con = sqlite3.connect(DB_PATH)
#     cur = con.cursor()
#     rows = cur.execute("SELECT * FROM destinations;").fetchall()
#     cols = [d[0] for d in cur.description]
#     con.close()
#     items = [dict(zip(cols, r)) for r in rows]
#     return {"destinations": items}


@app.get("/admin/refresh")
def refresh_data():
    """Force refresh Wikipedia data without restarting."""
    try:
        regenerate_data()
        return {"message": "Data refreshed successfully."}
    except Exception as e:
        return {"error": f"Refresh failed: {e}"}