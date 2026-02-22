# Lubimyczytac Scraper to Goodreads Pipeline

A Selenium-based data pipeline that reads a public Lubimyczytac profile library -> enriches book records with per-book metadata -> and exports a Goodreads-compatible CSV.
Tested wit GitHub actions.

## Project Structure

```text
.
|-- data_io/
|   |-- csv_utils.py         # CSV read/write and Goodreads export mapping
|   `-- __init__.py
|-- models/
|   |-- book.py              # Book dataclass and CSV schema
|   `-- __init__.py
|-- scraper/
|   |-- profile_scraper.py   # phase 1: list scraping from profile pages
|   |-- enrichment.py        # phase 2: per-book enrichment orchestration
|   |-- book_details.py      # phase 2: ISBN/original title extraction
|   `-- __init__.py
|-- dane/
|   |-- books.csv            # phase 1 output
|   |-- books_enriched.csv   # phase 2 output
|   `-- goodreads.csv        # phase 3 output
|-- tests/
|-- main.py                  # pipeline entry point
|-- config.example.ini       # link to user profile
|-- pyproject.toml
`-- LICENSE
```
## Scope

- Source: public Lubimyczytac profile library pages
- Output: normalized local CSV files, including Goodreads import format

## Stack

- Python 3
- Selenium + ChromeDriver
- uv (environment and dependency management)

## Setup (uv)

1. Install `uv` (if missing):

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Sync dependencies:

```bash
uv sync
```

3. Ensure Google Chrome and a compatible ChromeDriver are available in `PATH`.

## Configuration & Running

Rename exaple cofig and edit: `config.ini`:

```ini
[settings]
profile_url = https://lubimyczytac.pl/profil/YOUR_PROFILE_ID/YOUR_PROFILE_NAME
```

Run the pipeline entry point:

```bash
uv run python main.py
```

## Phase Artifacts Summary

- `dane/books.csv`: raw list scrape from profile pages (phase 1)
- `dane/books_enriched.csv`: per-book ISBN and original title enrichment (phase 2)
- `dane/goodreads.csv`: Goodreads import-ready export (phase 3)
## Pipeline Phases

### Phase 1: Profile Scraping

- Module: `scraper/profile_scraper.py`
- Entry function: `scrape_books(profile_url)`
- Input:
  - `profile_url` from `config.ini` (expanded in `main.py` with list query parameters)
- Processing:
  - Opens profile library pages in Selenium
  - Iterates pagination
  - Extracts row-level metadata (title, author, ratings, shelves, link, etc.)
  - Produces `Book` objects (domain model) before CSV serialization
- Output file:
  - `dane/books.csv` via `save_books_to_csv(...)`
- Shelf fields in this phase:
  - `Na półkach Główne`: primary state shelf (e.g. `Przeczytane`, `Teraz czytam`, `Chcę przeczytać`)
  - `Na półkach Pozostałe`: custom user shelves/tags (optional)

### Phase 2: Record Enrichment

- Modules: `scraper/enrichment.py`, `scraper/book_details.py`
- Entry function: `fill_isbn_and_original_titles(books)`
- Input file:
  - `dane/books.csv` loaded by `load_books_from_csv(...)`
- Processing:
  - Visits each book URL from column `Link`
  - Extracts ISBN and original title from the book detail page
  - Fills missing original title fallback with the Polish title
- Output file:
  - `dane/books_enriched.csv` via `save_books_to_csv(...)`

### Phase 3: Goodreads Conversion

- Module: `data_io/csv_utils.py`
- Entry function: `convert_books_to_goodreads(input_file, output_file)`
- Input file:
  - `dane/books_enriched.csv`
- Processing:
  - Maps Lubimyczytac columns to Goodreads import schema
  - `Na półkach Główne` -> Goodreads `Shelves`
  - `Na półkach Pozostałe` -> Goodreads `Bookshelves`
  - Writes Goodreads-required headers and transformed rows
- Output file:
  - `dane/goodreads.csv`

## License
This project is intended for educational use only. It is designed to demonstrate web scraping workflow design, CSV data processing, and multi-phase data transformation in Python.
This project is licensed under the MIT License. See `LICENSE` for details.

