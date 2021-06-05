class Book:
    def __init__(self, data) -> None:
        self.title = data['Title']
        self.authors = data['Authors']
        self.isbn10 = data['ISBN10']
        self.isbn13 = data['ISBN13']
        self.rating = data['Rating']
        self.readYear = data['ReadYear']
        self.progress = data['Progress']

    def print(self) -> str:
        return '## ![{0}](https://covers.openlibrary.org/b/isbn/{3}-S.jpg) {0}\n*{1}*\n\n[Massachusetts Library](https://library.minlib.net/search/i={3}) / [Open Library](http://openlibrary.org/isbn/{3}) / [Amazon](https://smile.amazon.com/dp/{2})'.format(self.title, ' & '.join(self.authors), self.isbn10, self.isbn13)
