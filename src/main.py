from book import Book
from author import Author
import json
from itertools import chain
from tqdm import tqdm
import datetime


def get_stats(books):
    stats = {}
    stats["num_books"] = len(books)
    stats["num_books_finished"] = len([x for x in books if x.progress > 0.7])
    stats["perc_books_finished"] = round(
        stats["num_books_finished"] * 100.0 / stats["num_books"], 2
    )
    stats["num_authors"] = len(
        set([z.print() for z in list(chain.from_iterable([x.authors for x in books]))])
    )
    stats["avg_rating"] = round(
        sum([x.rating for x in books if x.progress == 1.0 or x.rating > 0])
        / max(1, len([x for x in books if x.progress == 1.0 or x.rating > 0])),
        2,
    )
    return stats


def write_author_page(author, books):
    a = Author(author)
    author_stats = get_stats(books)
    with open("../authors/{0}.md".format(a.safe_name()), "w") as o:
        o.write(
            "# {0}:  Books Read {1} / {2}, Avg Rating: {3} {4}\n\n".format(
                a.print(),
                author_stats["num_books_finished"],
                author_stats["num_books"],
                author_stats["avg_rating"],
                " ".join([":star:" for i in range(round(author_stats["avg_rating"]))]),
            )
        )
        for book in books:
            o.write(book.print())
            o.write("\n")
        o.write("---\n")


def read_books():
    with open("../data.json", "r") as datafile:
        bdata = json.load(datafile)
        return bdata


def write_books(bdata):
    with open("../data.json", "w") as outfile:
        outfile.write(json.dumps(bdata, indent=4))


def print_header(years, cur_year):
    s = "# Year: "
    first = True
    for y in [x for (x, z) in sorted(years.items(), reverse=True)]:
        if first:
            if y == cur_year:
                s = s + "{0} ".format(y)
            else:
                s = s + "[{0}](../books/{1}) ".format(y, "" if y == 2024 else y)
            first = False
        else:
            if y == cur_year:
                s = s + "/ {0} ".format(y)
            else:
                s = s + "/ [{0}](../books/{1}) ".format(y, "" if y == 2024 else y)
    s = s + "\n"
    return s


def print_year(filename, books, yearly_stats, years, y):
    with open(filename, "w") as o:
        o.write(print_header(years, y))
        o.write(
            "# {0}: {1} Authors, {2} / {3} Books Read, Avg Rating: {4} {5}\n\n".format(
                y,
                yearly_stats[y]["num_authors"],
                yearly_stats[y]["num_books_finished"],
                yearly_stats[y]["num_books"],
                yearly_stats[y]["avg_rating"],
                " ".join(
                    [":star:" for i in range(round(yearly_stats[y]["avg_rating"]))]
                ),
            )
        )
        for book in books[y]:
            if book.readYear == y:
                o.write(book.print())
                o.write("\n")
        o.write("---\n")


def main():
    bdata = read_books()
    years = {}
    books = {}
    authorbooks = {}
    for b in tqdm(bdata["Books"], desc="Processing Books"):
        y = b["ReadYear"]
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
    yearly_stats = {}
    for y in years:
        yearly_stats[y] = get_stats(books[y])
        nrbooks[y] = len([x for x in books[y] if x.progress > 0.7])
        authors[y] = set(
            [
                z.print()
                for z in list(chain.from_iterable([x.authors for x in books[y]]))
            ]
        )

    current_year = True
    for y in tqdm(
        [x for (x, z) in sorted(years.items(), reverse=True)], desc="Book Lists"
    ):
        print_year("../books/{0}.md".format(y), books, yearly_stats, years, y)
        if current_year:
            print_year("../books/index.md", books, yearly_stats, years, y)
            current_year = False

    for author in tqdm(authorbooks, desc="Author Pages"):
        write_author_page(author, authorbooks[author])
    write_books(bdata)
    #   Generate Index page
    with open("../index.md", "w") as o:
        o.write("# Excellent Books\n")
        o.write("## [Book cover mosaic generator](/mosaic)\n")
        o.write("## Books read by year\n")
        for y in tqdm(
            [x for (x, z) in sorted(years.items(), reverse=True)], desc="Book Index"
        ):
            o.write("- [{0}](books/{0}.md)\n".format(y))
        for y in tqdm(
            [x for (x, z) in sorted(years.items(), reverse=True)], desc="Book Reviews"
        ):
            o.write("## Books with 5-star reviews, {0}\n".format(y))
            for b in books[y]:
                if "placeholder" not in b.thumbnail and b.rating > 4.0:
                    o.write('<img src="{0}" width=128>\n'.format(b.thumbnail))
            o.write("\n\n")
            o.write(
                "## Read completion: {0}%\n".format(
                    get_stats(books[y])["perc_books_finished"]
                )
            )
            for b in books[y]:
                if "placeholder" not in b.thumbnail and b.progress > 0.0:
                    o.write('<img src="{0}" width=128>\n'.format(b.thumbnail))
            o.write("\n---\n")

        o.write("#### &copy; {0} Bharath Krishnan".format(datetime.date.today().year))

    with open("../mosaic/index.html", "w") as o:
        o.write(
            '<!DOCTYPE html><html lang="en"><head><title>Book cover image mosaic generator</title><link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.classless.min.css"></head>\n'
        )
        o.write("<body><main><h1> Cover Image Mosaic Generator</h1>\n")
        o.write(
            '<p>Cover images courtesy <a href="https://openlibrary.org/">Open Library</a> & Google</p>\n'
        )
        o.write(
            "<p>Paste a list of ISBN13 ids in the form below to generate your own Cover Mosaic</p>\n"
        )
        o.write(
            '<form action="https://test-j7fvcrsyma-uc.a.run.app/" method="POST"><div><textarea name="ids" placeholder="9780441013593,9780316005401"></textarea></div><div><button>Mosaic!</button></div></form>\n'
        )
        o.write("</main></body></html>\n")


if __name__ == "__main__":
    main()
