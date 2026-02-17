"""
Module for enriching book data with additional information.

This module contains functions for adding ISBN and original title information
to book data that has been scraped from Lubimyczytac.pl.
"""
import time
import random
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from scraper.book_details import get_isbn_from_book_page

def _build_driver():
    """Create a Chrome driver with reduced background/browser logging noise."""
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Hide verbose ChromeDriver logs printed to terminal/stderr.
    service = Service(log_output=subprocess.DEVNULL)
    return webdriver.Chrome(options=chrome_options, service=service)


def fill_isbn_and_original_titles(books, min_delay=1.2, max_delay=2.8, log_every=5):
    """
    Enrich book data with ISBN and original titles.

    This function visits each book's page to extract additional information
    that is not available on the user's profile page.

    Args:
        books (list): A list of Book objects as returned by scrape_books()

    Returns:
        list: The same list of books, but with ISBN and original title fields populated
    """
    total = len(books)
    if total == 0:
        print("[Phase 2] No books to enrich.")
        return books

    if min_delay < 0:
        min_delay = 0
    if max_delay < min_delay:
        max_delay = min_delay

    # Reduce non-actionable browser logs in terminal.
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    driver = _build_driver()
    started_at = time.time()
    print(f"[Phase 2] Starting enrichment for {total} books...")

    for idx, book in enumerate(books, start=1):
        item_started = time.time()
        link = book.link
        isbn, original_title = get_isbn_from_book_page(driver, link)
        book.isbn = isbn
        used_fallback_title = False
        if original_title != 'BRAK':
            book.title = original_title
        else:
            book.title = book.polish_title
            used_fallback_title = True

        item_elapsed = time.time() - item_started
        if idx == 1 or idx % log_every == 0 or idx == total:
            elapsed = time.time() - started_at
            avg_per_item = elapsed / idx
            eta = avg_per_item * (total - idx)
            isbn_status = "yes" if isbn else "no"
            fallback_status = "yes" if used_fallback_title else "no"
            print(
                f"[Phase 2] {idx}/{total} | "
                f"ISBN: {isbn_status} | Fallback title: {fallback_status} | "
                f"last: {item_elapsed:.1f}s | ETA: {eta:.0f}s"
            )

        # delay between page loads (phase 2)
        time.sleep(random.uniform(min_delay, max_delay))

    driver.quit()
    print(f"[Phase 2] Enrichment completed in {time.time() - started_at:.1f}s.")
    return books
