"""
Scraper package for extracting book data from Lubimyczytac.pl.

This package contains modules for scraping book information from a user's profile
on Lubimyczytac.pl. It uses Selenium WebDriver to automate browser interactions
and extract data such as book titles, authors, ratings, and other metadata.
"""

from scraper.book_details import get_isbn_from_book_page
from scraper.profile_scraper import scrape_books
from scraper.enrichment import fill_isbn_and_original_titles

__all__ = ['get_isbn_from_book_page', 'scrape_books', 'fill_isbn_and_original_titles']