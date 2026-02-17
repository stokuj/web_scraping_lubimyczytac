"""
Main application module for the Lubimyczytac.pl web scraper.

This script serves as the entry point for the application. It coordinates the scraping process,
data processing, and file operations. The script reads configuration from config.ini,
scrapes book data from a user's profile on Lubimyczytac.pl, and saves the data to CSV files.
Various processing steps can be enabled or disabled by uncommenting the relevant code sections.
"""

from scraper import scrape_books, fill_isbn_and_original_titles
from table_utils import save_books_to_csv, load_books_from_csv, convert_books_to_goodreads
import configparser

if __name__ == "__main__":
    # Load profile URL from config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')
    profile_url = config.get('settings', 'profile_url')
    # Append parameters to the URL to access the user's book list
    profile_url += '/biblioteczka/lista?page=1&listId=booksFilteredList&findString=&kolejnosc=data-dodania&listType=list&objectId=605200&own=0&paginatorType=Standard'

    # STEP 1: Scrape book data and save to CSV
    # Uncomment these lines to scrape books from the user's profile
    # books = scrape_books(profile_url)
    # save_books_to_csv(books, 'dane/books.csv')
    # print(f"Scraped {len(books)} books and saved to 'dane/books.csv'")

    # STEP 2: Load book data from CSV
    # Uncomment these lines to load previously scraped books from CSV
    books_from_csv = load_books_from_csv('dane/books.csv')
    print(f"Loaded {len(books_from_csv)} books from 'dane/books.csv'")

    # STEP 3: Enrich book data with ISBN and original titles
    # Uncomment these lines to add ISBN and original titles to book data
    enriched_books = fill_isbn_and_original_titles(books_from_csv)

    # STEP 4: Save enriched book data to a new CSV file
    # Uncomment these lines to save the enriched book data
    save_books_to_csv(enriched_books, 'dane/books_enriched.csv')
    print(f"Saved enriched books to 'dane/books_enriched.csv'")

    # STEP 5: Convert book data to Goodreads format
    # Uncomment this line to convert the enriched book data to Goodreads format
    convert_books_to_goodreads('dane/books_enriched.csv', 'dane/goodreads.csv')
