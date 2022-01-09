from book import Book
from author import Author
import json
from itertools import chain

def write_author_page(author, books):
    a = Author(author)
    print(a.print_link())
    with open('../{0}.md'.format(a.safe_name()), 'w') as o:
        o.write('# Author {0},  Books Read {1} / {2}\n\n'.format(a.print(), len(books), len(books)))
        for book in books:
            o.write(book.print())
            o.write('\n')
        o.write('---\n')


def main():
    years = {}
    books = {}
    authorbooks = {}
    with open('../data.json', 'r') as datafile:
        bdata = json.load(datafile)
        for b in bdata['Books']:
            y = b['ReadYear']
            years[y] = 1
            if y not in books:
                books[y] = []
            book = Book(b)
            books[y].append(book)
            authors = book.authors
            for author in authors:
                author_name = author.print()
                if author_name not in authorbooks:
                    authorbooks[author_name] = []
                authorbooks[author_name].append(book)
        nrbooks = {}
        authors = {}
        for y in years:
            nrbooks[y] = len([x for x in books[y] if x.progress > 0.7])
            authors[y] = set([z.print() for z in list(chain.from_iterable([x.authors for x in books[y]]))])

        with open('../index.md', 'w') as o:
            for y in [x for (x,z) in sorted(years.items(), reverse=True)]:
                o.write('# {0}: {1} Authors, {2} / {3} Books Read \n\n'.format(y, len(authors[y]), nrbooks[y], len(books[y])))
                for book in books[y]:
                    if book.readYear == y:
                        o.write(book.print())
                        o.write('\n')
                o.write('---\n')
        for author in authorbooks:
            write_author_page(author, authorbooks[author])

if __name__ == '__main__':
    main()