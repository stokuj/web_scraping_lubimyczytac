"""
Module for scraping book data from a user's profile on Lubimyczytac.pl.

This module contains functions for navigating through a user's book list
and extracting detailed information about each book.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time

def scrape_books(profile_url):
    """
    Scrape book data from a user's profile on Lubimyczytac.pl.

    This function navigates through all pages of a user's book list,
    extracting detailed information about each book.

    Args:
        profile_url (str): URL of the user's profile page

    Returns:
        list: A list of lists, where each inner list contains data for one book
              with the following fields:
              [book_id, title, author, isbn, cycle, avg_rating, rating_count,
               readers, opinions, user_rating, book_link, read_date,
               shelves, self_shelves, original_title]
    """
    # Initialize Chrome WebDriver
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Headless mode if needed
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(profile_url)

    # Akceptacja ciasteczek, jeśli przycisk się pojawi
    try:
        accept_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Akcept")]'))
        )
        time.sleep(1)
        accept_btn.click()
    except:
        print("Nie znaleziono przycisku akceptacji ciasteczek.")

    all_books = []

    while True:
        # Czekaj aż książki się załadują
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'authorAllBooks__single'))
            )
        except TimeoutException:
            print("Brak książek na stronie — zakończono zbieranie.")
            break

        books = driver.find_elements(By.CLASS_NAME, 'authorAllBooks__single')

        for book in books:
            # ID książki
            try:
                book_id = book.get_attribute('id').replace('listBookElement', '')
            except:
                book_id = ''

            # Tytuł
            try:
                title_element = book.find_element(By.CLASS_NAME, 'authorAllBooks__singleTextTitle')
                title = title_element.text
                if isinstance(title, str):
                    title = title.strip()
            except:
                title = ''

            # Autor
            try:
                author = book.find_element(By.CLASS_NAME, 'authorAllBooks__singleTextAuthor').text.strip()
            except:
                author = ''

            # Link do książki
            try:
                book_link = book.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                book_link = ''

            # ISBN
            isbn = '' # Tymczasowo pusty, będzie uzupełniony później

            # Oryginalny tytuł
            original_title = '' # Tymczasowo pusty, będzie uzupełniony później

            # Cykl
            try:
                cycle_elem = book.find_elements(By.CLASS_NAME, 'listLibrary__info--cycles')
                cycle = cycle_elem[0].text[6:] if cycle_elem and len(cycle_elem[0].text) > 6 else ''
            except:
                cycle = ''

            # Średnia ocena
            try:
                rating_elements = book.find_elements(By.CLASS_NAME, 'listLibrary__rating')
                avg_rating = rating_elements[0].find_element(
                    By.CLASS_NAME, 'listLibrary__ratingStarsNumber'
                ).text.strip()
            except:
                avg_rating = ''

            # Ocena użytkownika
            try:
                user_rating = rating_elements[1].find_element(
                    By.CLASS_NAME, 'listLibrary__ratingStarsNumber'
                ).text.strip()
            except:
                user_rating = ''

            # Liczba ocen
            try:
                rating_count = book.find_element(
                    By.CLASS_NAME, 'listLibrary__ratingAll'
                ).text.replace('ocen', '').strip()
            except:
                rating_count = ''

            # Liczba czytelników i liczba opinii
            try:
                for ro in book.find_elements(By.CLASS_NAME, 'small.grey'):
                    text = ro.text.strip()
                    if 'Czytelnicy:' in text:
                        readers = text.replace('Czytelnicy:', '').strip()
                    elif 'Opinie:' in text:
                        opinions = text.replace('Opinie:', '').strip()
            except:
                readers = ''
                opinions = '' # zostają domyślne puste stringi

            # Data przeczytania
            try:
                read_date_elem = book.find_element(By.CLASS_NAME, 'authorAllBooks__read-dates')
                read_date = read_date_elem.text.replace('Przeczytał:', '').strip()
            except:
                read_date = '' # zostają domyślne puste stringi

            # Półki (shelves) oraz półki użytkownika (self_shelves)
            try:
                shelf_elem = book.find_element(By.CLASS_NAME, 'authorAllBooks__singleTextShelfRight')
                all_shelf_names = [a.text.strip() for a in shelf_elem.find_elements(By.TAG_NAME, 'a')]

                standard_shelves = {"Przeczytane", "Teraz czytam", "Chcę przeczytać"}
                shelves = ', '.join([s for s in all_shelf_names if s in standard_shelves])
                self_shelves = ', '.join([s for s in all_shelf_names if s not in standard_shelves])
            except:
                shelves = ''
                self_shelves = ''


            # Dodaj dane o książce do listy
            all_books.append([
                book_id,               # ID
                title,                 # Tytuł
                author,                # Autor
                isbn,                  # ISBN
                cycle,                 # Cykl
                avg_rating,            # Średnia ocena
                rating_count,          # Liczba ocen
                readers,               # Czytelnicy
                opinions,              # Opinie
                user_rating,           # Ocena użytkownika
                book_link,             # Link
                read_date,             # Data przeczytania
                shelves,               # Na półkach Główne
                self_shelves,          # Na półkach Pozostałe
                original_title         # Polski Tytuł (czyli na końcu!)
            ])

        # Przejście do następnej strony
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'next-page')
            if 'disabled' in next_button.get_attribute('class'):
                break
            next_button.click()
            time.sleep(1)  # Poczekaj na załadowanie strony
        except:
            break  # Nie ma przycisku lub już ostatnia strona

    driver.quit()
    return all_books