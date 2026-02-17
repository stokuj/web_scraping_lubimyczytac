# Web Scraper using Selenium

Python scraper for collecting books from a public Lubimyczytac.pl profile and exporting data to CSV, including a Goodreads-compatible file.

## Supported Site

- Lubimyczytac.pl profile library pages

## Tech Stack

- Python 3
- Selenium
- ChromeDriver
- pytest

## Project Structure

```text

```

## Installation

1. Clone the repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Chrome and a matching ChromeDriver available in PATH.

## Configuration

Edit `config.ini`:

```ini
[settings]
profile_url = https://lubimyczytac.pl/profil/YOUR_PROFILE/
```

## Usage

Run:

```bash
python main.py
```

Current default flow in `main.py` expects `dane/books.csv` to already exist, then enriches it and generates `dane/goodreads.csv`.

## Testing

Run tests with:

```bash
python -m pytest -v
```

If `pytest` is missing:

```bash
pip install pytest
```

## Output Files

- `dane/books.csv`: scraped profile books
- `dane/books_enriched.csv`: records enriched with ISBN/original title
- `dane/goodreads.csv`: Goodreads import format
