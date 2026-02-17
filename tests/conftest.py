import os
import sys
from unittest.mock import MagicMock

import pytest

from models import Book

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def sample_books():
    return [
        Book(
            book_id="1",
            polish_title="Tytuł Polski 1",
            author="Autor 1",
            isbn="ISBN1",
            cycle="Cykl 1",
            avg_rating="4.5",
            rating_count="100",
            readers="200",
            opinions="50",
            user_rating="5",
            link="http://example.com/book1",
            read_date="2023-01-01",
            main_shelves="Przeczytane",
            other_shelves="Fantasy, Sci-Fi",
            title="Original Title 1",
        ),
        Book(
            book_id="2",
            polish_title="Tytuł Polski 2",
            author="Autor 2",
            isbn="ISBN2",
            cycle="Cykl 2",
            avg_rating="4.0",
            rating_count="200",
            readers="300",
            opinions="75",
            user_rating="4",
            link="http://example.com/book2",
            read_date="2023-02-01",
            main_shelves="Chcę przeczytać",
            other_shelves="Horror, Mystery",
            title="Original Title 2",
        ),
    ]


@pytest.fixture
def temp_csv_file(tmp_path):
    return os.path.join(tmp_path, "test_books.csv")


@pytest.fixture
def mock_driver():
    driver = MagicMock()
    isbn_meta = MagicMock()
    isbn_meta.get_attribute.return_value = "9781234567890"
    driver.find_element.return_value = isbn_meta
    return driver
