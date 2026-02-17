"""
Module for scraping book data from a user's profile on Lubimyczytac.pl.

This module contains functions for navigating through a user's book list
and extracting detailed information about each book.
"""

import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from models import Book


STANDARD_SHELVES = {
    "Przeczytane",
    "Teraz czytam",
    "Chce przeczytac",
    "Chcę przeczytać",
}


def _clean_text(value):
    if isinstance(value, str):
        return value.strip()
    return ""


def _safe_element_text(element):
    text = _clean_text(getattr(element, "text", ""))
    if text:
        return text
    try:
        return _clean_text(element.get_attribute("textContent"))
    except Exception:
        return ""


def _first_text(book, locators):
    for by, value in locators:
        try:
            element = book.find_element(by, value)
        except Exception:
            continue

        text = _safe_element_text(element)
        if text:
            return text
    return ""


def _get_card_lines(driver, book):
    raw = _clean_text(book.text)
    if raw:
        return [line.strip() for line in raw.splitlines() if line.strip()]

    # Some cards return empty .text even when content exists in the DOM.
    try:
        raw = _clean_text(
            driver.execute_script(
                "return arguments[0].innerText || arguments[0].textContent || '';",
                book,
            )
        )
    except Exception:
        raw = ""

    return [line.strip() for line in raw.splitlines() if line.strip()]


def _is_metadata_line(line):
    lower = line.lower()
    if lower.startswith("cykl:"):
        return True
    if "ocen" in lower:
        return True
    if lower.startswith("czytelnicy:") or lower.startswith("opinie:"):
        return True
    if lower.startswith("przeczyta"):
        return True
    if line in STANDARD_SHELVES:
        return True
    if re.match(r"^\d+[,.]\d$", line):
        return True
    return False


def _is_ui_noise_line(line):
    lower = line.lower()
    noise_markers = [
        "na półkach",
        "na p\u00f3\u0142kach",
        "dodaj na p\u00f3\u0142k",
        "dodaj na półk",
        "kup ksi\u0105\u017ck",
        "kup książk",
        "/ 10",
    ]
    return any(marker in lower for marker in noise_markers)


def scrape_books(profile_url, log_every=20):
    """
    Scrape book data from a user's profile on Lubimyczytac.pl.

    This function navigates through all pages of a user's book list,
    extracting detailed information about each book.

    Args:
        profile_url (str): URL of the user's profile page
        log_every (int): Print progress every N scraped books

    Returns:
        list: A list of Book objects.
    """
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(profile_url)

    started_at = time.time()
    page_no = 0
    total_books = 0
    debug_dumped = False
    print("[Phase 1] Starting profile scraping...")

    # Cookie consent if available.
    try:
        accept_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Akcept")]'))
        )
        time.sleep(1)
        accept_btn.click()
    except Exception:
        print("[Phase 1] Cookie consent button not found.")

    all_books = []

    while True:
        page_no += 1
        try:
            WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.CLASS_NAME, "authorAllBooks__single"))
            )
        except TimeoutException:
            print("[Phase 1] No books found on page, stopping.")
            break

        books = driver.find_elements(By.CLASS_NAME, "authorAllBooks__single")
        page_books = 0

        for book in books:
            card_lines = _get_card_lines(driver, book)

            # ID
            try:
                book_id = _clean_text(book.get_attribute("id")).replace("listBookElement", "")
            except Exception:
                book_id = ""

            # Link
            book_link = ""
            try:
                anchors = book.find_elements(By.XPATH, './/a[contains(@href, "/ksiazka/")]')
                if anchors:
                    book_link = _clean_text(anchors[0].get_attribute("href"))
            except Exception:
                book_link = ""

            if not book_link:
                try:
                    book_link = _clean_text(book.find_element(By.TAG_NAME, "a").get_attribute("href"))
                except Exception:
                    book_link = ""

            # Title and author
            title = _first_text(
                book,
                [
                    (By.CLASS_NAME, "authorAllBooks__singleTextTitle"),
                    (By.CSS_SELECTOR, '[class*="singleTextTitle"]'),
                    (By.CSS_SELECTOR, '[class*="listLibrary__title"]'),
                ],
            )
            author = _first_text(
                book,
                [
                    (By.CLASS_NAME, "authorAllBooks__singleTextAuthor"),
                    (By.CSS_SELECTOR, '[class*="singleTextAuthor"]'),
                    (By.CSS_SELECTOR, '[class*="listLibrary__author"]'),
                ],
            )

            # Ratings and cycle
            cycle = ""
            avg_rating = ""
            user_rating = ""
            rating_count = ""
            try:
                cycle_elem = book.find_elements(By.CLASS_NAME, "listLibrary__info--cycles")
                cycle = _safe_element_text(cycle_elem[0]) if cycle_elem else ""
                if cycle.lower().startswith("cykl:"):
                    cycle = cycle.split(":", 1)[1].strip()
            except Exception:
                cycle = ""

            try:
                rating_elements = book.find_elements(By.CLASS_NAME, "listLibrary__rating")
                if rating_elements:
                    avg_rating = _safe_element_text(
                        rating_elements[0].find_element(By.CLASS_NAME, "listLibrary__ratingStarsNumber")
                    )
                if len(rating_elements) > 1:
                    user_rating = _safe_element_text(
                        rating_elements[1].find_element(By.CLASS_NAME, "listLibrary__ratingStarsNumber")
                    )
            except Exception:
                pass

            try:
                rating_count = _safe_element_text(book.find_element(By.CLASS_NAME, "listLibrary__ratingAll"))
                rating_count = rating_count.replace("ocen", "").strip()
            except Exception:
                rating_count = ""

            # Readers and opinions
            readers = ""
            opinions = ""
            try:
                for ro in book.find_elements(By.CLASS_NAME, "small.grey"):
                    text = _safe_element_text(ro)
                    if "Czytelnicy:" in text:
                        readers = text.replace("Czytelnicy:", "").strip()
                    elif "Opinie:" in text:
                        opinions = text.replace("Opinie:", "").strip()
            except Exception:
                pass

            # Read date
            try:
                read_date_elem = book.find_element(By.CLASS_NAME, "authorAllBooks__read-dates")
                read_date = _safe_element_text(read_date_elem)
                read_date = read_date.replace("Przeczytał:", "").replace("Przeczytal:", "").strip()
            except Exception:
                read_date = ""

            # Shelves
            shelves = ""
            self_shelves = ""
            try:
                shelf_elem = book.find_element(By.CLASS_NAME, "authorAllBooks__singleTextShelfRight")
                all_shelf_names = [
                    _clean_text(a.text)
                    for a in shelf_elem.find_elements(By.TAG_NAME, "a")
                    if _clean_text(a.text)
                ]
                shelves = ", ".join([s for s in all_shelf_names if s in STANDARD_SHELVES])
                self_shelves = ", ".join([s for s in all_shelf_names if s not in STANDARD_SHELVES])
            except Exception:
                pass

            # Fallback parse from card lines.
            if card_lines:
                if not cycle:
                    for line in card_lines:
                        if line.lower().startswith("cykl:"):
                            cycle = line.split(":", 1)[1].strip()
                            break

                if not rating_count:
                    for line in card_lines:
                        if "ocen" in line.lower():
                            rating_count = line.lower().replace("ocen", "").strip()
                            break

                if not readers:
                    for line in card_lines:
                        if line.startswith("Czytelnicy:"):
                            readers = line.replace("Czytelnicy:", "").strip()
                            break

                if not opinions:
                    for line in card_lines:
                        if line.startswith("Opinie:"):
                            opinions = line.replace("Opinie:", "").strip()
                            break

                if not read_date:
                    for line in card_lines:
                        if line.lower().startswith("przeczyta"):
                            read_date = line.split(":", 1)[1].strip() if ":" in line else ""
                            break

                rating_candidates = [line for line in card_lines if re.match(r"^\d+[,.]\d$", line)]
                if not avg_rating and rating_candidates:
                    avg_rating = rating_candidates[0]
                if not user_rating and len(rating_candidates) > 1:
                    user_rating = rating_candidates[1]

                if not shelves:
                    found_standard = [line for line in card_lines if line in STANDARD_SHELVES]
                    if found_standard:
                        shelves = ", ".join(dict.fromkeys(found_standard))
                # Do not infer self_shelves from raw card lines.
                # It produces UI noise like "Na półkach", "KUP KSIĄŻKĘ", ratings etc.

                content_lines = [line for line in card_lines if not _is_metadata_line(line)]
                if not title and content_lines:
                    title = content_lines[0]
                if not author and len(content_lines) > 1:
                    author = content_lines[1]

            if self_shelves:
                cleaned = []
                for part in [p.strip() for p in self_shelves.split(",") if p.strip()]:
                    if not _is_ui_noise_line(part):
                        cleaned.append(part)
                self_shelves = ", ".join(dict.fromkeys(cleaned))

            # Last fallback for title from URL slug.
            if not title and book_link:
                try:
                    slug = book_link.rstrip("/").rsplit("/", 1)[-1]
                    title = slug.replace("-", " ")
                except Exception:
                    pass

            if (not title and not author) and (not debug_dumped):
                print(f"[Phase 1][debug] Empty title/author for first card. Lines: {card_lines[:10]}")
                debug_dumped = True

            # Filled in phase 2.
            isbn = ""
            original_title = ""

            all_books.append(
                Book(
                    book_id=book_id,
                    polish_title=title,
                    author=author,
                    isbn=isbn,
                    cycle=cycle,
                    avg_rating=avg_rating,
                    rating_count=rating_count,
                    readers=readers,
                    opinions=opinions,
                    user_rating=user_rating,
                    link=book_link,
                    read_date=read_date,
                    main_shelves=shelves,
                    other_shelves=self_shelves,
                    title=original_title,
                )
            )

            page_books += 1
            total_books += 1
            if log_every and (total_books == 1 or total_books % log_every == 0):
                elapsed = time.time() - started_at
                rate = total_books / elapsed if elapsed > 0 else 0
                print(
                    f"[Phase 1] page {page_no} | scraped total: {total_books} | "
                    f"rate: {rate:.2f} books/s"
                )

        print(f"[Phase 1] page {page_no} done | page books: {page_books} | total: {total_books}")

        try:
            next_button = driver.find_element(By.CLASS_NAME, "next-page")
            if "disabled" in _clean_text(next_button.get_attribute("class")):
                break
            next_button.click()
            time.sleep(1)
        except Exception:
            break

    driver.quit()
    print(f"[Phase 1] Scraping completed in {time.time() - started_at:.1f}s.")
    return all_books
