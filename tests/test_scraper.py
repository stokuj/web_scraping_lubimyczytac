from unittest.mock import MagicMock, patch

from scraper import fill_isbn_and_original_titles, get_isbn_from_book_page, scrape_books


@patch("scraper.book_details.WebDriverWait")
def test_get_isbn_from_book_page_valid_url(mock_wait, mock_driver):
    mock_wait.return_value.until.return_value = MagicMock()

    isbn_meta = MagicMock()
    isbn_meta.get_attribute.return_value = "9781234567890"
    details_section = MagicMock()
    details_section.get_attribute.return_value = """
    <dt>Tytuł oryginału:</dt>
    <dd>Original Book Title</dd>
    """

    mock_driver.find_element.side_effect = [isbn_meta, details_section]
    isbn, original_title = get_isbn_from_book_page(mock_driver, "http://example.com/book")

    assert isbn == "9781234567890"
    assert original_title == "Original Book Title"


def test_get_isbn_from_book_page_invalid_url(mock_driver):
    isbn, original_title = get_isbn_from_book_page(mock_driver, "")
    assert isbn == ""
    assert original_title == "BRAK"


@patch("scraper.enrichment.webdriver.Chrome")
@patch("scraper.enrichment.get_isbn_from_book_page")
def test_fill_isbn_and_original_titles(mock_get_isbn, mock_chrome, sample_books):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    mock_get_isbn.side_effect = [
        ("9781234567890", "Original Title 1"),
        ("9780987654321", "BRAK"),
    ]

    enriched_books = fill_isbn_and_original_titles(sample_books, min_delay=0, max_delay=0, log_every=1000)

    assert enriched_books[0].isbn == "9781234567890"
    assert enriched_books[0].title == "Original Title 1"
    assert enriched_books[1].isbn == "9780987654321"
    assert enriched_books[1].title == "Tytuł Polski 2"

    mock_get_isbn.assert_any_call(mock_driver, "http://example.com/book1")
    mock_get_isbn.assert_any_call(mock_driver, "http://example.com/book2")


@patch("scraper.profile_scraper.webdriver.Chrome")
@patch("scraper.profile_scraper.WebDriverWait")
@patch("scraper.profile_scraper.time")
def test_scrape_books(mock_time, mock_wait, mock_chrome):
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver
    mock_wait.return_value.until.return_value = MagicMock()

    book1 = MagicMock()
    book1.get_attribute.return_value = "listBookElement1"
    book1.text = "Tytuł Polski 1\nAutor 1"

    def find_element_side_effect(by, value):
        if value == "authorAllBooks__singleTextTitle":
            m = MagicMock()
            m.text = "Tytuł Polski 1"
            return m
        if value == "authorAllBooks__singleTextAuthor":
            m = MagicMock()
            m.text = "Autor 1"
            return m
        if value == "authorAllBooks__read-dates":
            m = MagicMock()
            m.text = "Przeczytał: 2023-01-01"
            return m
        if value == "listLibrary__ratingAll":
            m = MagicMock()
            m.text = "100 ocen"
            return m
        if value == "authorAllBooks__singleTextShelfRight":
            shelf = MagicMock()
            shelf.find_elements.return_value = [MagicMock(text="Przeczytane")]
            return shelf
        return MagicMock()

    def find_elements_side_effect(by, value):
        if by == "xpath" and "/ksiazka/" in value:
            anchor = MagicMock()
            anchor.get_attribute.return_value = "http://example.com/book1"
            return [anchor]
        if value == "listLibrary__info--cycles":
            return [MagicMock(text="Cykl: Cykl 1")]
        if value == "listLibrary__rating":
            avg_el = MagicMock()
            avg_child = MagicMock()
            avg_child.text = "4.5"
            avg_el.find_element.return_value = avg_child
            return [avg_el]
        if value == "small.grey":
            return [MagicMock(text="Czytelnicy: 200"), MagicMock(text="Opinie: 50")]
        return []

    book1.find_element.side_effect = find_element_side_effect
    book1.find_elements.side_effect = find_elements_side_effect

    mock_driver.find_elements.return_value = [book1]
    next_button = MagicMock()
    next_button.get_attribute.return_value = "disabled"
    mock_driver.find_element.return_value = next_button

    books = scrape_books("http://example.com/profile", log_every=1000)

    assert len(books) == 1
    assert books[0].book_id == "1"
    assert books[0].polish_title == "Tytuł Polski 1"
    assert books[0].author == "Autor 1"
    assert books[0].link == "http://example.com/book1"
    mock_chrome.assert_called_once()
    mock_driver.get.assert_called_once_with("http://example.com/profile")
    mock_driver.quit.assert_called_once()
