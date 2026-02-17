"""
Module for extracting detailed book information from Lubimyczytac.pl.
"""

import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _extract_original_title(section_html):
    if not section_html:
        return "BRAK"

    patterns = [
        r"Tytuł oryginału:\s*</dt>\s*<dd>(.*?)</dd>",
        r"TytuĹ‚ oryginaĹ‚u:\s*</dt>\s*<dd>(.*?)</dd>",
    ]

    for pattern in patterns:
        match = re.search(pattern, section_html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    return "BRAK"


def get_isbn_from_book_page(driver, url):
    """
    Extract ISBN and original title from a book page.

    Returns:
        tuple[str, str]: (isbn, original_title)
    """
    if not url or not url.startswith("http"):
        print(f"Invalid URL: {url}")
        return "", "BRAK"

    isbn = ""
    original_title = "BRAK"

    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "head")))

        try:
            isbn_meta = driver.find_element(By.XPATH, '//meta[@property="books:isbn"]')
            isbn = (isbn_meta.get_attribute("content") or "").strip()
        except Exception:
            isbn = ""

        try:
            details_section = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "book-details"))
            )
            section_content = details_section.get_attribute("innerHTML") or ""
            original_title = _extract_original_title(section_content)
        except TimeoutException:
            print(f"Book details section not found: {url}")
            original_title = "BRAK"

    except Exception as exc:
        print(f"Error while loading {url}: {exc}")
        original_title = "BRAK"

    return isbn, original_title
