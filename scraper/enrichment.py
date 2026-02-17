"""
Module for enriching book data with additional information.

This module contains functions for adding ISBN and original title information
to book data that has been scraped from Lubimyczytac.pl.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scraper.book_details import get_isbn_from_book_page

def fill_isbn_and_original_titles(books):
    """
    Enrich book data with ISBN and original titles.

    This function visits each book's page to extract additional information
    that is not available on the user's profile page.

    Args:
        books (list): A list of book data as returned by scrape_books()

    Returns:
        list: The same list of books, but with ISBN and original title fields populated
    """
    # Initialize Chrome WebDriver
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)

    for book in books:
        link = book[10]
        isbn, original_title = get_isbn_from_book_page(driver, link)
        book[3] = isbn
        if original_title != 'BRAK':
            book[14] = original_title
        else:
            book[14] = book[1]


    driver.quit()
    return books