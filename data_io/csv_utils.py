"""
Utility module for CSV operations.
"""

import csv
import os

from models import Book, CSV_HEADERS


def save_books_to_csv(books, filename):
    """Save book data to a CSV file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADERS)
        for book in books:
            if isinstance(book, Book):
                writer.writerow(book.to_row())
            else:
                writer.writerow(Book.from_row(book).to_row())


def load_books_from_csv(filename):
    """Load book data from CSV into Book objects."""
    books = []
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            books.append(Book.from_row(row))
    return books


def convert_books_to_goodreads(input_file, output_file):
    """Convert book data to Goodreads CSV format."""
    books = load_books_from_csv(input_file)

    fieldnames = [
        "Title",
        "Polish Title",
        "Author",
        "ISBN",
        "My Rating",
        "Average Rating",
        "Publisher",
        "Binding",
        "Year Published",
        "Original Publication Year",
        "Date Read",
        "Date Added",
        "Shelves",
        "Bookshelves",
        "My Review",
    ]

    with open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for book in books:
            writer.writerow(
                {
                    "Title": book.title,
                    "Polish Title": book.polish_title,
                    "Author": book.author,
                    "ISBN": book.isbn,
                    "My Rating": book.user_rating,
                    "Average Rating": book.avg_rating,
                    "Publisher": "",
                    "Binding": "",
                    "Year Published": "",
                    "Original Publication Year": "",
                    "Date Read": book.read_date,
                    "Date Added": "",
                    "Shelves": book.main_shelves,
                    "Bookshelves": book.other_shelves,
                    "My Review": "",
                }
            )
