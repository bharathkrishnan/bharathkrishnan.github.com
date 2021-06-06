from book import Book
import json
from itertools import chain

def main():
    books = []
    with open('../data.json', 'r') as datafile:
        bdata = json.load(datafile)
        for b in bdata['Books']:
            books.append(Book(b))
        nrbooks = len([x for x in books if x.progress > 0.7])
        authors = set(list(chain.from_iterable([x.authors for x in books])))

        with open('../index.md', 'w') as o:
            o.write('# 2021: {0} Authors, {1} / {2} Books Read \n\n'.format(len(authors), nrbooks, len(books)))
            for book in books:
                o.write(book.print())
                o.write('\n')

if __name__ == '__main__':
    main()