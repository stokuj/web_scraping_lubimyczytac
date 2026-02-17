import csv
import os

from models import Book
from table_utils import convert_books_to_goodreads, load_books_from_csv, save_books_to_csv


def test_save_and_load_books(sample_books, temp_csv_file):
    save_books_to_csv(sample_books, temp_csv_file)
    assert os.path.exists(temp_csv_file)

    loaded_books = load_books_from_csv(temp_csv_file)
    assert len(loaded_books) == len(sample_books)
    assert all(isinstance(book, Book) for book in loaded_books)
    assert loaded_books[0] == sample_books[0]
    assert loaded_books[1] == sample_books[1]


def test_convert_books_to_goodreads(sample_books, temp_csv_file, tmp_path):
    save_books_to_csv(sample_books, temp_csv_file)
    goodreads_file = os.path.join(tmp_path, "goodreads.csv")
    convert_books_to_goodreads(temp_csv_file, goodreads_file)
    assert os.path.exists(goodreads_file)

    with open(goodreads_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert len(rows) == len(sample_books)
    assert rows[0]["Title"] == "Original Title 1"
    assert rows[0]["Polish Title"] == "Tytuł Polski 1"
    assert rows[0]["Author"] == "Autor 1"
    assert rows[0]["ISBN"] == "ISBN1"
    assert rows[0]["My Rating"] == "5"
    assert rows[0]["Average Rating"] == "4.5"
    assert rows[0]["Date Read"] == "2023-01-01"
    assert rows[0]["Shelves"] == "Przeczytane"
    assert rows[0]["Bookshelves"] == "Fantasy, Sci-Fi"


def test_convert_books_to_goodreads_other_shelves_optional(tmp_path):
    input_file = os.path.join(tmp_path, "books.csv")
    output_file = os.path.join(tmp_path, "goodreads.csv")

    row = Book(
        book_id="9",
        polish_title="Test",
        author="Author",
        isbn="",
        cycle="",
        avg_rating="",
        rating_count="",
        readers="",
        opinions="",
        user_rating="",
        link="http://example.com/book9",
        read_date="",
        main_shelves="Przeczytane",
        other_shelves="",
        title="Test",
    )
    save_books_to_csv([row], input_file)
    convert_books_to_goodreads(input_file, output_file)

    with open(output_file, mode="r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert rows[0]["Bookshelves"] == ""
