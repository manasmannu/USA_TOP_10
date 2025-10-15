# UsaTop10 — Angular Frontend + Python Seeder (SQLite)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Web%20Framework-brightgreen)
![Angular](https://img.shields.io/badge/Frontend-Angular-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Wikipedia](https://img.shields.io/badge/API-Wikipedia-blueviolet)
![License](https://img.shields.io/badge/License-MIT-yellow)

A simple demo that showcases **Top 10 U.S. destinations** (fixed list) with short descriptions, best months to visit, tags, coordinates, and hero images.  
The data is **fetched from Wikipedia** by a Python script and stored in a local **SQLite** database (`db.sqlite3`). Images are saved into the Angular app’s assets so the UI can display them.

> **Note:** The “Top 10” list is _hardcoded_ in the seeder. You can change it by editing `DESTINATIONS` and `DEFAULTS` in `backend-python/generate_seed_from_wikipedia.py`.

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
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Original Angular CLI Notes](#original-angular-cli-notes)

---

## Demo

To start the backend server

<p align="center">
  <img src="https://github.com/user-attachments/assets/329921d9-4659-4063-b536-c050c57ca8ff" 
       alt="Server" width="65%">
</p>

To start the frontend server

<p align="center">
  <img src="https://github.com/user-attachments/assets/b7573e12-8ea9-494b-a366-14805a57c21e" 
       alt="Server" width="65%">
</p>

The application will be available on http://localhost:4200/

<p align="center">
  <img src="https://github.com/user-attachments/assets/9f8d567e-a489-40bf-9ec5-35f7aa377f44" 
       alt="Application" width="65%">
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/4d27146a-8952-4b04-91be-783f8fa8b5fb" 
       alt="Application" width="65%">
</p>

Size adjust automatically in the mobile view

<p align="center">
  <img src="https://github.com/user-attachments/assets/271024e9-bcfb-4377-9c22-dac597bf30da" 
       alt="Application" width="50%">
</p>

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

uvicorn app:app --reload --port 8000

# 2) Frontend: install & run
cd ../frontend-angular/usa-top10
npm install
ng serve --port 4200
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

4. **Start the backend server**
   uvicorn app:app --reload --port 8000

---

### 2) Frontend (Angular) – Install & Run

1. **Install dependencies**

   ```bash
   cd ../frontend-angular/usa-top10
   npm install
   ```

2. **Run the dev server**

   ```bash
   ng serve --port 4200
   ```

3. Open the app at: http://localhost:4200

4. **Production build**
   ```bash
   ng build
   ```
   Artifacts will be in `dist/`. Deploy as you normally would.

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

---

## FAQ

**Q: Does the app auto-discover “Top 10” cities?**  
A: No. The list is hardcoded. Edit `DESTINATIONS` to change it.

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
