"""
Utility module for data processing and CSV operations.
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
    """Load book data from a CSV file as Book objects."""
    books = []
    with open(filename, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            books.append(Book.from_row(row))
    return books


def convert_books_to_goodreads(input_file, output_file):
    """Convert Lubimyczytac CSV data into Goodreads import format."""
    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

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

            for row in reader:
                shelves = row.get("Na półkach Główne", "") or row.get("Na pĂłĹ‚kach GĹ‚owne", "")
                bookshelves = row.get("Na półkach Pozostałe", "") or row.get("Na pĂłĹ‚kach PozostaĹ‚e", "")

                goodreads_row = {
                    "Title": row.get("Tytuł", "") or row.get("TytuĹ‚", ""),
                    "Polish Title": row.get("Polski Tytuł", "") or row.get("Polski TytuĹ‚", ""),
                    "Author": row.get("Autor", ""),
                    "ISBN": row.get("ISBN", ""),
                    "My Rating": row.get("Ocena użytkownika", "") or row.get("Ocena uĹĽytkownika", ""),
                    "Average Rating": row.get("Średnia ocena", "") or row.get("Ĺšrednia ocena", ""),
                    "Publisher": "",
                    "Binding": "",
                    "Year Published": "",
                    "Original Publication Year": "",
                    "Date Read": row.get("Data przeczytania", ""),
                    "Date Added": "",
                    "Shelves": shelves,
                    "Bookshelves": bookshelves,
                    "My Review": "",
                }

                writer.writerow(goodreads_row)
