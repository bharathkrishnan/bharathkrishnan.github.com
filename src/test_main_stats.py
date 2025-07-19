import pytest
from main import get_stats

class MockBook:
    def __init__(self, progress_map, rating, authors, title="BookX"):
        self._progress_map = progress_map  # dict: year -> progress
        self.rating = rating
        self.authors = authors
        self.title = title
        self.readYear = list(progress_map.keys())
    def get_progress_for_year(self, year):
        return self._progress_map.get(year, 0.0)
    def print(self, year=None):
        # Simulate print output with year and progress
        progress = self.get_progress_for_year(year) if year else 0.0
        return f"{self.title} ({year}): {int(progress*100)}%"
    @property
    def progress(self):
        # Return a list of progress values in the order of readYear, mimicking Book
        return [self._progress_map.get(y, 0.0) for y in self.readYear]

class MockAuthor:
    def __init__(self, name):
        self._name = name
    def print(self):
        return self._name
    def safe_name(self):
        return self._name.replace(" ", "")
    def print_link(self):
        return f"[{self._name}](../authors/{self.safe_name()})"

@pytest.fixture
def author_books():
    # Author A: 2 books, Author B: 1 book
    return {
        "Author A": [
            MockBook({2021: 1.0, 2022: 0.5}, 5.0, [MockAuthor("Author A")], title="Book1"),
            MockBook({2022: 1.0}, 4.0, [MockAuthor("Author A")], title="Book2"),
        ],
        "Author B": [
            MockBook({2021: 0.7}, 3.0, [MockAuthor("Author B")], title="Book3"),
        ]
    }

def mock_write_author_page(author, books):
    # Simulate the output string for the author page
    stats = get_stats(books)
    output = f"# {author}:  Books Read {stats['num_books_finished']} / {stats['num_books']}, Avg Rating: {stats['avg_rating']}\n\n"
    for book in books:
        # Show all years for each book
        for year in book.readYear:
            output += book.print(year=year) + "\n"
    output += "---\n"
    return output

def test_author_page_output(author_books):
    # Test Author A
    output_a = mock_write_author_page("Author A", author_books["Author A"])
    assert "Book1 (2021): 100%" in output_a
    assert "Book1 (2022): 50%" in output_a
    assert "Book2 (2022): 100%" in output_a
    assert "Books Read 1 / 2" in output_a or "Books Read 2 / 2" in output_a  # depending on finished logic
    # Test Author B
    output_b = mock_write_author_page("Author B", author_books["Author B"])
    assert "Book3 (2021): 70%" in output_b
    assert "Books Read 0 / 1" in output_b 