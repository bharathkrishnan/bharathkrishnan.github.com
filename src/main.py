from book import Book, get_year_group
from author import Author
import json
from itertools import chain
from tqdm import tqdm
import datetime


def get_stats(books, year=None):
    stats = {}
    stats["num_books"] = len(books)
    if year is not None:
        if year.endswith('s'):  # It's a decade
            # For decades, check if any of the original years in the decade have progress
            stats["num_books_finished"] = len([x for x in books if any(x.get_progress_for_year(orig_year) > 0.7 for orig_year in x.readYear)])
            finished_books = [x for x in books if any(x.get_progress_for_year(orig_year) == 1.0 or x.rating > 0 for orig_year in x.readYear)]
        else:
            stats["num_books_finished"] = len([x for x in books if x.get_progress_for_year(year) > 0.7])
            finished_books = [x for x in books if x.get_progress_for_year(year) == 1.0 or x.rating > 0]
    else:
        stats["num_books_finished"] = len([x for x in books if x.progress and x.progress[0] > 0.7])
        finished_books = [x for x in books if x.progress and (x.progress[0] == 1.0 or x.rating > 0)]
    stats["perc_books_finished"] = round(
        stats["num_books_finished"] * 100.0 / stats["num_books"], 2
    ) if stats["num_books"] > 0 else 0.0
    stats["num_authors"] = len(
        set([z.print() for z in list(chain.from_iterable([x.authors for x in books]))])
    )
    stats["avg_rating"] = round(
        sum([x.rating for x in finished_books]) / max(1, len(finished_books)),
        2,
    ) if books else 0.0
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
    
    # Use the same sorting logic as in main()
    def year_sort_key(year):
        if year.endswith('s'):  # It's a decade
            decade_num = int(year[:-1])  # Remove 's' and convert to int
            return (0, decade_num)  # Decades come first
        else:
            year_num = int(year)
            return (1, year_num)  # Individual years come after decades
    
    for y in [x for x in sorted(years.keys(), key=year_sort_key, reverse=True)]:
        if first:
            if y == cur_year:
                s = s + "{0} ".format(y)
            else:
                s = s + "[{0}](../books/{1}) ".format(y, y)
            first = False
        else:
            if y == cur_year:
                s = s + "/ {0} ".format(y)
            else:
                s = s + "/ [{0}](../books/{1}) ".format(y, y)
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
            # For decades, don't pass the year to book.print() since it's a decade string
            if y.endswith('s'):
                o.write(book.print())
            else:
                o.write(book.print(year=y))
            o.write("\n")
        o.write("---\n")


def main():
    bdata = read_books()
    years = {}
    books = {}
    authorbooks = {}
    for b in tqdm(bdata["Books"], desc="Processing Books"):
        # Always treat ReadYear as a list
        ryears = b["ReadYear"] if isinstance(b["ReadYear"], list) else [b["ReadYear"]]
        book = Book(b)
        for idx, y in enumerate(ryears):
            # Group years into decades for years < 2020, keep individual years for 2020+
            year_group = get_year_group(y)
            years[year_group] = 1
            if year_group not in books:
                books[year_group] = []
            books[year_group].append(book)
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
        yearly_stats[y] = get_stats(books[y], year=y)
        # For decade grouping, we need to check progress differently
        if y.endswith('s'):  # It's a decade
            # For decades, check if any of the original years in the decade have progress
            nrbooks[y] = len([x for x in books[y] if any(x.get_progress_for_year(orig_year) > 0.7 for orig_year in x.readYear)])
        else:
            nrbooks[y] = len([x for x in books[y] if x.get_progress_for_year(y) > 0.7])
        authors[y] = set(
            [
                z.print()
                for z in list(chain.from_iterable([x.authors for x in books[y]]))
            ]
        )

    # Sort years properly: decades first (newest to oldest), then individual years (newest to oldest)
    def year_sort_key(year):
        if year.endswith('s'):  # It's a decade
            decade_num = int(year[:-1])  # Remove 's' and convert to int
            return (0, decade_num)  # Decades come first
        else:
            year_num = int(year)
            return (1, year_num)  # Individual years come after decades
    
    current_year = True
    for y in tqdm(
        [x for x in sorted(years.keys(), key=year_sort_key, reverse=True)], desc="Book Lists"
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
        # o.write("## [Book cover mosaic generator](/mosaic)\n")
        o.write("## Books read by year\n")
        for y in tqdm(
            [x for x in sorted(years.keys(), key=year_sort_key, reverse=True)], desc="Book Index"
        ):
            o.write("- [{0}](books/{0}.md)\n".format(y))
        for y in tqdm(
            [x for x in sorted(years.keys(), key=year_sort_key, reverse=True)], desc="Book Reviews"
        ):
            o.write("## Books with 5-star reviews, {0}\n".format(y))
            for b in books[y]:
                if "placeholder" not in b.thumbnail and b.rating > 4.0:
                    o.write('<img src="{0}" width=128>\n'.format(b.thumbnail))
            o.write("\n\n")
            o.write(
                "## Read completion: {0}%\n".format(
                    get_stats(books[y], year=y)["perc_books_finished"]
                )
            )
            for b in books[y]:
                if "placeholder" not in b.thumbnail and b.get_progress_for_year(y) > 0.0:
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
            '<form action="https://test-j7fvcrsyma-uc.a.run.app/" method="POST"><div><textarea name="ids" placeholder="9780802163622,9781250303561401"></textarea></div><div><button>Mosaic!</button></div></form>\n'
        )
        o.write("</main></body></html>\n")


if __name__ == "__main__":
    main()
