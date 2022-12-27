from author import Author
import requests

class Book:
    def __init__(self, data) -> None:
        self.title = data['Title']
        self.authors = [Author(x) for x in data['Authors']]
        self.isbn10 = data['ISBN10']
        self.isbn13 = data['ISBN13']
        self.rating = data['Rating']
        self.readYear = data['ReadYear']
        self.progress = data['Progress']
        if 'ThumbNail' not in data:
            self.thumbnail = self.get_thumbnail()
            if self.thumbnail != 'None':
                data['ThumbNail'] = self.thumbnail
        else:
            self.thumbnail = data['ThumbNail']
    
    def get_thumbnail(self):
        olurl = 'https://covers.openlibrary.org/b/isbn/{0}-S.jpg'.format(self.isbn13) 
        gburl = 'https://www.googleapis.com/books/v1/volumes?q=isbn:{0}'.format(self.isbn13.replace('-', ''))
        r = requests.get(olurl)
        if r.status_code == 200:
            return olurl
        print(gburl)
        print()
        print('--')
        gbr = requests.get(gburl)
        if gbr.status_code == 200:
            print(gbr.json())
            if gbr.json()['totalItems'] > 0:
                return gbr.json()['items'][0]['volumeInfo']['imageLinks']['smallThumbnail']

    # def print(self) -> str:
    #     return '## ![{0}](https://covers.openlibrary.org/b/isbn/{3}-S.jpg) {0}\n*{1}*\n\n[Massachusetts Library](https://library.minlib.net/search/i={3}) / [Open Library](http://openlibrary.org/isbn/{3}) / [Local Book Shop](https://bookshop.org/books/{4}/{3}) / [Amazon](https://smile.amazon.com/dp/{2})\n\n![{5}%](https://progress-bar.dev/{5}) \n\n{6}\n'.format(self.title, ' & '.join([a.print_link() for a in self.authors]), self.isbn10, self.isbn13, '-'.join(self.title.lower().split()), str(round(self.progress*100)), ' '.join([':star:' for i in range(round(self.rating))]))
    def print(self) -> str:
        return '## ![{0}]({7}) {0}\n*{1}*\n\n[Massachusetts Library](https://library.minlib.net/search/i={3}) / [Open Library](http://openlibrary.org/isbn/{3}) / [Local Book Shop](https://bookshop.org/books/{4}/{3}) / [Amazon](https://smile.amazon.com/dp/{2})\n\n![{5}%](https://progress-bar.dev/{5}) \n\n{6}\n'.format(self.title, ' & '.join([a.print_link() for a in self.authors]), self.isbn10, self.isbn13, '-'.join(self.title.lower().split()), str(round(self.progress*100)), ' '.join([':star:' for i in range(round(self.rating))]), self.thumbnail)
