import pytest
from unittest.mock import MagicMock, patch
from scraper import get_isbn_from_book_page, fill_isbn_and_original_titles, scrape_books

@patch('scraper.book_details.WebDriverWait')
def test_get_isbn_from_book_page_valid_url(mock_wait, mock_driver):
    """Test getting ISBN and original title from a valid book page."""
    # Mock WebDriverWait.until to simulate page loading
    mock_wait.return_value.until.return_value = MagicMock()

    # Mock find_element for ISBN meta tag
    isbn_meta = MagicMock()
    isbn_meta.get_attribute.return_value = "9781234567890"
    mock_driver.find_element.return_value = isbn_meta

    # Mock find_element for details section
    details_section = MagicMock()
    details_section.get_attribute.return_value = """
    <dt>Tytuł oryginału:</dt>
    <dd>Original Book Title</dd>
    """
    mock_wait.return_value.until.return_value = details_section

    # Call the function
    isbn, original_title = get_isbn_from_book_page(mock_driver, "http://example.com/book")

    # Verify results
    assert isbn == "9781234567890"
    assert original_title == "Original Book Title"

def test_get_isbn_from_book_page_invalid_url(mock_driver):
    """Test getting ISBN and original title from an invalid URL."""
    # Call the function with an invalid URL
    isbn, original_title = get_isbn_from_book_page(mock_driver, "")

    # Verify results
    assert isbn == ""
    assert original_title == "BRAK"

@patch('scraper.enrichment.webdriver.Chrome')
@patch('scraper.enrichment.get_isbn_from_book_page')
def test_fill_isbn_and_original_titles(mock_get_isbn, mock_chrome, sample_books):
    """Test filling ISBN and original titles for books."""
    # Mock Chrome driver
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    # Mock get_isbn_from_book_page to return different values for each book
    mock_get_isbn.side_effect = [
        ("9781234567890", "Original Title 1"),
        ("9780987654321", "BRAK")
    ]

    # Call the function
    enriched_books = fill_isbn_and_original_titles(sample_books)

    # Verify results
    assert enriched_books[0][3] == "9781234567890"  # ISBN for first book
    assert enriched_books[0][14] == "Original Title 1"  # Original title for first book
    assert enriched_books[1][3] == "9780987654321"  # ISBN for second book
    assert enriched_books[1][14] == "Tytuł Polski 2"  # Original title for second book (falls back to Polish title)

    # Verify get_isbn_from_book_page was called with correct URLs
    mock_get_isbn.assert_any_call(mock_driver, "http://example.com/book1")
    mock_get_isbn.assert_any_call(mock_driver, "http://example.com/book2")

@patch('scraper.profile_scraper.webdriver.Chrome')
@patch('scraper.profile_scraper.WebDriverWait')
@patch('scraper.profile_scraper.time')
def test_scrape_books(mock_time, mock_wait, mock_chrome):
    """Test scraping books from a user's profile."""
    # Mock Chrome driver
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    # Mock WebDriverWait.until to simulate page loading
    mock_wait.return_value.until.return_value = MagicMock()

    # Create mock book elements
    book1 = MagicMock()
    book1.get_attribute.return_value = "listBookElement1"  # ID

    # Create a more comprehensive side_effect function for find_element
    def find_element_side_effect(by, value):
        if value == "authorAllBooks__singleTextTitle":
            mock = MagicMock()
            mock.text = "Tytuł Polski 1"
            return mock
        elif value == "authorAllBooks__singleTextAuthor":
            mock = MagicMock()
            mock.text = "Autor 1"
            return mock
        elif value == "authorAllBooks__read-dates":
            mock = MagicMock()
            mock.text = "Przeczytał: 2023-01-01"
            return mock
        elif value == "listLibrary__ratingAll":
            mock = MagicMock()
            mock.text = "100 ocen"
            return mock
        elif value == "authorAllBooks__singleTextShelfRight":
            return MagicMock()
        elif value == "a":
            mock = MagicMock()
            mock.get_attribute = lambda attr: "http://example.com/book1"
            return mock
        elif value == "listLibrary__ratingStarsNumber":
            mock = MagicMock()
            mock.text = "4.5"
            return mock
        else:
            return MagicMock()

    book1.find_element.side_effect = find_element_side_effect

    book1.find_elements.side_effect = lambda by, value: {
        "listLibrary__info--cycles": [MagicMock(text="Cykl: Cykl 1")],
        "listLibrary__rating": [
            MagicMock(),  # avg_rating element
            MagicMock()   # user_rating element
        ],
        "small.grey": [
            MagicMock(text="Czytelnicy: 200"),
            MagicMock(text="Opinie: 50")
        ]
    }.get(value, [])

    # Mock find_elements for book elements
    mock_driver.find_elements.return_value = [book1]

    # Mock find_element for next button
    next_button = MagicMock()
    next_button.get_attribute.return_value = "disabled"  # Only one page
    mock_driver.find_element.return_value = next_button

    # Call the function
    books = scrape_books("http://example.com/profile")

    # Verify results
    assert len(books) == 1
    assert books[0][0] == "1"  # ID
    assert books[0][1] == "Tytuł Polski 1"  # Title
    assert books[0][2] == "Autor 1"  # Author
    assert books[0][10] == "http://example.com/book1"  # Link

    # Verify Chrome was initialized and used correctly
    mock_chrome.assert_called_once()
    mock_driver.get.assert_called_once_with("http://example.com/profile")
    mock_driver.quit.assert_called_once()
