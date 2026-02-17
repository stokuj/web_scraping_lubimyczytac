"""
Module for extracting detailed book information from Lubimyczytac.pl.

This module contains functions for extracting ISBN and original title
from a book's page on Lubimyczytac.pl.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_isbn_from_book_page(driver, url):
    """
    Extract ISBN and original title from a book's page.

    Args:
        driver (WebDriver): Selenium WebDriver instance
        url (str): URL of the book page

    Returns:
        tuple: A tuple containing (isbn, original_title)
            - isbn (str): The ISBN of the book, or empty string if not found
            - original_title (str): The original title of the book, or 'BRAK' if not found
    """
    # Return empty data if URL is invalid
    if not url or not url.startswith("http"):
        print(f"❌ Nieprawidłowy URL: {url}")
        return '', 'BRAK'

    isbn = ''
    original_title = 'BRAK'
    try:
        driver.get(url)

        # czekamy, aż strona się załaduje
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'head'))
        )

        # --- pobranie ISBN ---
        try:
            isbn_meta = driver.find_element(
                By.XPATH, '//meta[@property="books:isbn"]'
            )
            isbn = isbn_meta.get_attribute("content").strip()
        except:
            isbn = ''

        # Próba pobrania całej sekcji szczegółów
        try:
            # Oczekiwanie na załadowanie sekcji szczegółów
            details_section = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "book-details"))
            )

            # Pobierz całą zawartość HTML sekcji
            section_content = details_section.get_attribute("innerHTML")
            # print("=== ZAWARTOŚĆ SEKCJI SZCZEGÓŁÓW ===")
            # print(section_content)
            # print("===================================")
            start = section_content.find("Tytuł oryginału:")
            if start != -1:
                start = section_content.find("<dd>", start)
                end = section_content.find("</dd>", start)
                original_title = section_content[start+4:end].strip()
                #print(original_title)


        except TimeoutException:
            print(f"🔍 Nie znaleziono sekcji szczegółów książki na stronie {url}")
            original_title = "BRAK"

        except TimeoutException:
            # nie znaleziono dt -> zostawiamy default 'BRAK'
            print(f"🔍 Nie znaleziono sekcji 'Tytuł oryginału' na stronie {url}")

    except Exception as e:
        print(f"Błąd pobierania danych z {url}: {e}")
        original_title = 'test'       
    return isbn, original_title