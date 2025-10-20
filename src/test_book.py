import pytest
from book import Book

@pytest.fixture
def single_year_data():
    return {
        "Title": "Test Book",
        "Authors": ["Author A"],
        "ISBN10": "1234567890",
        "ISBN13": "9781234567890",
        "ReadYear": 2021,
        "Progress": 1.0,
        "Rating": 4.0,
        "ThumbNail": "https://example.com/cover.jpg"
    }

@pytest.fixture
def multi_year_data():
    return {
        "Title": "Test Book Multi",
        "Authors": ["Author B"],
        "ISBN10": "0987654321",
        "ISBN13": "9780987654321",
        "ReadYear": [2021, 2023],
        "Progress": [1.0, 0.5],
        "Rating": 5.0,
        "ThumbNail": "https://example.com/cover2.jpg"
    }

def test_book_init_single_year(single_year_data):
    book = Book(single_year_data)
    assert book.readYear == [2021]
    assert book.progress == [1.0]
    assert book.get_progress_for_year(2021) == 1.0
    assert book.get_progress_for_year(2022) == 0.0

def test_book_init_multi_year(multi_year_data):
    book = Book(multi_year_data)
    assert book.readYear == [2021, 2023]
    assert book.progress == [1.0, 0.5]
    assert book.get_progress_for_year(2021) == 1.0
    assert book.get_progress_for_year(2023) == 0.5
    assert book.get_progress_for_year(2022) == 0.0

def test_book_print_single_year(single_year_data):
    book = Book(single_year_data)
    output = book.print(year=2021)
    assert "Test Book" in output
    assert "2021" in output
    assert "100%" in output

def test_book_print_multi_year(multi_year_data):
    book = Book(multi_year_data)
    output_2021 = book.print(year=2021)
    output_2023 = book.print(year=2023)
    assert "Test Book Multi" in output_2021
    assert "2021" in output_2021
    assert "100%" in output_2021
    assert "50%" in output_2023
    assert "2023" in output_2023

def test_book_thumbnail_fallback():
    data = {
        "Title": "No Thumb",
        "Authors": ["Author C"],
        "ISBN10": "1111111111",
        "ISBN13": "9781111111111",
        "ReadYear": 2022,
        "Progress": 0.7,
        "Rating": 3.0,
        "ThumbNail": "null"
    }
    book = Book(data)
    assert book.thumbnail.startswith("https://")


def test_book_thumbnail_normalizes_openlibrary():
    data = {
        "Title": "Open Library Thumb",
        "Authors": ["Author D"],
        "ISBN10": "2222222222",
        "ISBN13": "9782222222222",
        "ReadYear": 2020,
        "Progress": 1.0,
        "Rating": 4.0,
        "ThumbNail": "https://covers.openlibrary.org/b/isbn/9782222222222-L.jpg"
    }
    book = Book(data)
    assert book.thumbnail.endswith("-M.jpg")
    assert data["ThumbNail"].endswith("-M.jpg")
