from book import Book
import json
from itertools import chain

def main():
    years = {}
    books = {}
    with open('../data.json', 'r') as datafile:
        bdata = json.load(datafile)
        for b in bdata['Books']:
            y = b['ReadYear']
            years[y] = 1
            if y not in books:
                books[y] = []
            books[y].append(Book(b))
        nrbooks = {}
        authors = {}
        for y in years:
            nrbooks[y] = len([x for x in books[y] if x.progress > 0.7])
            authors[y] = set(list(chain.from_iterable([x.authors for x in books[y]])))

        with open('../index.md', 'w') as o:
            for y in [x for (x,z) in sorted(years.items(), reverse=True)]:
                o.write('# {0}: {1} Authors, {2} / {3} Books Read \n\n'.format(y, len(authors[y]), nrbooks[y], len(books[y])))
                for book in books[y]:
                    if book.readYear == y:
                        o.write(book.print())
                        o.write('\n')
                o.write('---\n')
if __name__ == '__main__':
    main()