# UsaTop10 — Angular Frontend + Python Seeder (SQLite)

A simple demo that showcases **Top 10 U.S. destinations** (fixed list) with short descriptions, best months to visit, tags, coordinates, and hero images.  
The data is **fetched from Wikipedia** by a Python script and stored in a local **SQLite** database (`db.sqlite3`). Images are saved into the Angular app’s assets so the UI can display them.

> **Note:** The “Top 10” list is *hardcoded* in the seeder. You can change it by editing `DESTINATIONS` and `DEFAULTS` in `backend-python/generate_seed_from_wikipedia.py`.

---

## Table of Contents
- [Demo](#Demo)
- [What This App Does](#what-this-app-does)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start (TL;DR)](#quick-start-tldr)
- [Detailed Setup](#detailed-setup)
  - [1) Backend (Python) – Virtual Env & Seeder](#1-backend-python--virtual-env--seeder)
  - [2) Frontend (Angular) – Install & Run](#2-frontend-angular--install--run)
- [Wiring the “Refresh” Button (Optional)](#wiring-the-refresh-button-optional)
  - [Express/Node example](#expressnode-example)
  - [Flask (Python) example](#flask-python-example)
- [Inspecting the SQLite DB](#inspecting-the-sqlite-db)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Original Angular CLI Notes](#original-angular-cli-notes)


---
## Demo
To start the backend server
https://github.com/user-attachments/assets/329921d9-4659-4063-b536-c050c57ca8ff

To start the frontend server
https://github.com/user-attachments/assets/b7573e12-8ea9-494b-a366-14805a57c21e

The application will be available on http://localhost:4200/
https://github.com/user-attachments/assets/9f8d567e-a489-40bf-9ec5-35f7aa377f44

https://github.com/user-attachments/assets/4d27146a-8952-4b04-91be-783f8fa8b5fb

Size adjust automatically in the mobile view
https://github.com/user-attachments/assets/271024e9-bcfb-4377-9c22-dac597bf30da


## What This App Does

- Shows a curated list of **10 destinations** in a modern Angular UI.
- Python script calls the **Wikipedia APIs** (Search + Summary) to pull:
  - A short summary (first paragraph)
  - **Coordinates** (lat/lon) when available
  - A **thumbnail image** (downloaded as a hero image)
- Saves data into **SQLite** (`db.sqlite3`, table: `destinations`).
- Saves images under the Angular app’s assets:  
  `frontend-angular/usa-top10/src/assets/images/`
- Provides a **Refresh** workflow so you can re-seed data again later.

> Emojis in Angular templates (like `🔄 Refresh`) are safe, but for production consider a proper icon library (Angular Material or FontAwesome) for consistency and accessibility.

---

## Architecture

```
backend-python/
  generate_seed_from_wikipedia.py   # seeder: Wikipedia -> SQLite + images
db.sqlite3             # created/overwritten by the seeder
seed.sql               # generated SQL (DROP/CREATE + INSERTs)

frontend-angular/
  usa-top10/
    src/
      assets/
        images/          # hero images downloaded by the seeder
      app/               # Angular components/services

```

---

## Prerequisites

- **Python** 3.9+ (3.10 recommended)
- **Node.js** 18+ and **npm** 9+ (or use nvm to manage versions)
- **Angular CLI** (global):
  ```bash
  npm install -g @angular/cli
  ```
- (Optional) **SQLite CLI** for inspecting DB from terminal:
  ```bash
  # macOS (Homebrew)
  brew install sqlite
  # Ubuntu/Debian
  sudo apt-get install sqlite3
  ```
- (Optional) **DB Browser for SQLite** (GUI): https://sqlitebrowser.org

---

## Quick Start (TL;DR)

```bash
# 1) Backend: create venv, install, seed
cd backend-python
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

pip install requests

# set your contact email for Wikipedia API etiquette
# macOS/Linux:
export CONTACT_EMAIL="your_email@example.com"
# Windows PowerShell:
# $env:CONTACT_EMAIL="your_email@example.com"

python generate_seed_from_wikipedia.py

# 2) Frontend: install & run
cd ../frontend-angular/usa-top10
npm install
ng serve
# open http://localhost:4200
```

---

## Detailed Setup

### 1) Backend (Python) – Virtual Env & Seeder

1. **Create and activate a virtual environment**

   **macOS/Linux**
   ```bash
   cd backend-python
   python -m venv .venv
   source .venv/bin/activate
   ```

   **Windows (PowerShell)**
   ```powershell
   cd backend-python
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**
   ```bash
   pip install requests
   ```
   `sqlite3` ships with Python; no extra install required.

3. **Set a contact email (environment variable)**  
   Wikipedia asks API users to identify a contact in the `User-Agent`.  
   **Never hardcode personal emails in code**—use an env var instead.

   **macOS/Linux**
   ```bash
   export CONTACT_EMAIL="your_email@example.com"
   ```

   **Windows (PowerShell)**
   ```powershell
   $env:CONTACT_EMAIL="your_email@example.com"
   ```

4. **Run the seeder**
   ```bash
   python generate_seed_from_wikipedia.py
   ```

   This will:
   - Query Wikipedia for each destination.
   - Save hero images into:
     `../frontend-angular/usa-top10/src/assets/images/`
   - Generate `seed.sql`.
   - Create/overwrite `db.sqlite3` with a `destinations` table and data.

5. **(Optional) Verify data quickly**
   ```bash
   sqlite3 db.sqlite3
   .tables
   SELECT id, name, state, region, hero_image FROM destinations LIMIT 10;
   .exit
   ```

> To change the list of places, edit `DESTINATIONS` and `DEFAULTS` in the seeder and re-run it.

---

### 2) Frontend (Angular) – Install & Run

1. **Install dependencies**
   ```bash
   cd ../frontend-angular/usa-top10
   npm install
   ```

2. **Run the dev server**
   ```bash
   ng serve
   ```

3. Open the app at: http://localhost:4200

4. **Production build**
   ```bash
   ng build
   ```
   Artifacts will be in `dist/`. Deploy as you normally would.

---

## Wiring the “Refresh” Button (Optional)

If your UI has a **Refresh** button, wire it to a backend endpoint that triggers the seeder. Two minimal examples:

### Express/Node example

```js
// server.js
import express from "express";
import { spawn } from "child_process";
const app = express();

app.post("/api/refresh-seed", (req, res) => {
  // run the Python seeder
  const child = spawn("python", ["backend-python/generate_seed_from_wikipedia.py"], {
    env: { ...process.env, CONTACT_EMAIL: process.env.CONTACT_EMAIL || "anonymous@example.com" },
  });

  child.on("close", (code) => {
    if (code === 0) return res.status(200).send({ ok: true });
    res.status(500).send({ ok: false, code });
  });
});

app.listen(3000, () => console.log("Server on :3000"));
```

Angular service/button (example):

```ts
// refresh.service.ts
refresh() {
  return this.http.post<void>('/api/refresh-seed', {});
}
```

```html
<!-- refresh.component.html -->
<button (click)="onRefresh()" [disabled]="isLoading">
  <span *ngIf="!isLoading">🔄 Refresh</span>
  <span *ngIf="isLoading" aria-live="polite">Refreshing…</span>
</button>
```

```ts
// refresh.component.ts
isLoading = false;
onRefresh() {
  this.isLoading = true;
  this.refreshService.refresh().subscribe({
    next: () => (this.isLoading = false),
    error: () => (this.isLoading = false),
  });
}
```

### Flask (Python) example

```python
# app.py
import os, subprocess
from flask import Flask, jsonify

app = Flask(__name__)

@app.post("/api/refresh-seed")
def refresh_seed():
    env = os.environ.copy()
    env.setdefault("CONTACT_EMAIL", "anonymous@example.com")
    code = subprocess.call(
        ["python", "backend-python/generate_seed_from_wikipedia.py"],
        env=env
    )
    if code == 0:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "code": code}), 500

if __name__ == "__main__":
    app.run(port=3000, debug=True)
```

---

## Inspecting the SQLite DB

**Command line**:
```bash
sqlite3 db.sqlite3
.tables
.schema destinations
SELECT * FROM destinations LIMIT 5;
.exit
```

**GUI**: Open `db.sqlite3` in **DB Browser for SQLite** to browse/edit visually.

---

## Troubleshooting

- **Images not showing in UI**
  - Ensure the seeder wrote files to  
    `frontend-angular/usa-top10/src/assets/images/`
  - Make sure Angular uses correct relative asset paths.

- **Wikipedia rate limit / 429**
  - Seeder retries automatically on 429/5xx.
  - Ensure `CONTACT_EMAIL` is set.
  - Avoid hammering refresh repeatedly.

- **SQLite “database is locked”**
  - Close other processes using `db.sqlite3`.
  - Delete `db.sqlite3` and re-run the seeder if necessary.

- **Emoji renders as empty box**
  - Your font may not support it. Consider Material/FontAwesome icons.

---

## FAQ

**Q: Does the app auto-discover “Top 10” cities?**  
A: No. The list is hardcoded. Edit `DESTINATIONS` to change it.

**Q: Is my email exposed publicly?**  
A: No. It’s only sent in the HTTP header to Wikipedia. Use the `CONTACT_EMAIL` env var rather than hardcoding into the script.

**Q: Can I point this to a different frontend path for images?**  
A: Yes. Update `IMG_DIR` in `generate_seed_from_wikipedia.py` to your desired folder.

---

## Original Angular CLI Notes

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 20.3.5.

### Development server
```bash
ng serve
```
Open `http://localhost:4200/` in your browser.

### Code scaffolding
```bash
ng generate component component-name
ng generate --help
```

### Building
```bash
ng build
```

### Unit tests
```bash
ng test
```

### End-to-end tests
```bash
ng e2e
```

For more on Angular CLI, see the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli).
