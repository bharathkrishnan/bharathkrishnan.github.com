from book import Book
import json

def main():
    books = []
    with open('../data.json', 'r') as datafile:
        bdata = json.load(datafile)
        for b in bdata['Books']:
            books.append(Book(b))
        with open('../index.md', 'w') as o:
            o.write('# 2021 Books\n\n')
            for book in books:
                o.write(book.print())
                o.write('\n')

if __name__ == '__main__':
    main()