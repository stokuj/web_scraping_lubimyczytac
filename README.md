# Lubimyczytac Scraper to Goodreads Pipeline

A Selenium-based data pipeline that reads a public Lubimyczytac profile library, enriches book records with per-book metadata, and exports a Goodreads-compatible CSV.

## Scope

- Source: public Lubimyczytac profile library pages
- Output: normalized local CSV files, including Goodreads import format

## Educational Purpose

This project is intended for educational use only. It is designed to demonstrate web scraping workflow design, CSV data processing, and multi-phase data transformation in Python.

## Stack

- Python 3
- Selenium + ChromeDriver
- pytest
- uv (environment and dependency management)

## Project Layout

```text
.
|-- scraper/
|   |-- profile_scraper.py   # phase 1: list scraping from profile pages
|   |-- enrichment.py        # phase 2: per-book enrichment orchestration
|   |-- book_details.py      # phase 2: ISBN/original title extraction
|   `-- __init__.py
|-- models/
|   |-- book.py              # Book dataclass and CSV schema
|   `-- __init__.py
|-- dane/
|   |-- books.csv            # phase 1 output
|   |-- books_enriched.csv   # phase 2 output
|   `-- goodreads.csv        # phase 3 output
|-- tests/
|-- main.py                  # pipeline entry point
|-- table_utils.py           # CSV I/O + Goodreads mapping
|-- config.ini
|-- pyproject.toml
`-- LICENSE
```

## Setup (uv)

1. Install `uv` (if missing):

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Sync dependencies:

```bash
uv sync
```

Install all dependency groups (including `dev`, e.g. `pytest`) when needed:

```bash
uv sync --all-groups
```

3. Ensure Google Chrome and a compatible ChromeDriver are available in `PATH`.

## Configuration

Set your profile URL in `config.ini`:

```ini
[settings]
profile_url = https://lubimyczytac.pl/profil/YOUR_PROFILE/
```

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

- Module: `table_utils.py`
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

## Running

Run the pipeline entry point:

```bash
uv run python main.py
```

Current default flow in `main.py` executes phases 2 and 3 (expects `dane/books.csv` to already exist). Phase 1 lines are present and can be enabled in code.

## Tests

```bash
uv run pytest -v
```

## Phase Artifacts Summary

- `dane/books.csv`: raw list scrape from profile pages (phase 1)
- `dane/books_enriched.csv`: per-book ISBN and original title enrichment (phase 2)
- `dane/goodreads.csv`: Goodreads import-ready export (phase 3)

## License

This project is licensed under the MIT License. See `LICENSE` for details.


## Is Na półkach Pozostałe Required?

Short answer: not strictly required for a valid Goodreads import.

- Keep it if you want to preserve custom shelf organization from Lubimyczytac.
- You can leave it empty and the pipeline still works; Goodreads Bookshelves will be blank.
- If your goal is only title/author/rating transfer, this field can be treated as optional.

