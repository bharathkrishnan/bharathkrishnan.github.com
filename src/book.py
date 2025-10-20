from author import Author
import requests


def _normalize_openlibrary_thumbnail(url):
    """Convert Open Library large thumbnails (-L.jpg) to medium (-M.jpg)."""
    if isinstance(url, str) and "openlibrary.org" in url and "-L.jpg" in url:
        return url.replace("-L.jpg", "-M.jpg")
    return url


def get_year_group(year):
    """
    Convert a year to its appropriate group (decade for years < 2020, year for 2020+)
    """
    if isinstance(year, str) and year.endswith('s'):
        # Already a decade string like "1990s"
        return year
    
    year_int = int(year)
    if year_int >= 2020:
        return str(year_int)
    else:
        # Group into decade
        decade = (year_int // 10) * 10
        return f"{decade}s"


class Book:
    def __init__(self, data) -> None:
        self.title = data["Title"]
        self.authors = [Author(x) for x in data["Authors"]]
        self.isbn10 = data["ISBN10"]
        self.isbn13 = data["ISBN13"].replace('-', '')
        self.rating = data["Rating"]
        # Always treat ReadYear as a list for backward compatibility
        ry = data["ReadYear"]
        if isinstance(ry, list):
            raw_years = ry
        else:
            raw_years = [ry]
        # Normalize year values to integers when possible (e.g., "2025" -> 2025)
        self.readYear = [
            int(y) if isinstance(y, str) and y.isdigit() else y for y in raw_years
        ]
        # Always treat Progress as a list for backward compatibility
        prog = data["Progress"]
        if isinstance(prog, list):
            self.progress = prog
        else:
            self.progress = [prog]
        # Map year (normalized to int when possible) to progress.
        # If a decade string like "2000s" appears in data, expand it to years 2000..2009.
        self.year_progress = {}
        for i, y in enumerate(self.readYear):
            prog = self.progress[i] if i < len(self.progress) else 0.0
            if isinstance(y, str) and y.endswith('s') and y[:-1].isdigit():
                decade_start = int(y[:-1])
                for yy in range(decade_start, decade_start + 10):
                    # keep the max progress if multiple entries set the same year
                    self.year_progress[yy] = max(self.year_progress.get(yy, 0.0), prog)
            else:
                y_key = int(y) if isinstance(y, str) and y.isdigit() else y
                self.year_progress[y_key] = prog
        thumb = _normalize_openlibrary_thumbnail(data.get("ThumbNail")) if "ThumbNail" in data else None
        if thumb is None or thumb == "null":
            self.thumbnail = _normalize_openlibrary_thumbnail(self.get_thumbnail())
            if self.thumbnail is not None:
                data["ThumbNail"] = self.thumbnail
            else:
                self.thumbnail = "https://via.placeholder.com/128x202?text={0}".format(
                    "+".join(self.title.split(" "))
                )
        else:
            self.thumbnail = thumb
            data["ThumbNail"] = self.thumbnail

    def get_progress_for_year(self, year):
        # Handle decade strings like "2010s" - check if any year in the decade has progress
        if isinstance(year, str) and year.endswith('s'):
            # For decades, check if any of the original years in the decade have progress
            decade_start = int(year[:-1])  # Remove 's' to get decade start
            decade_years = range(decade_start, decade_start + 10)
            return max(self.year_progress.get(y, 0.0) for y in decade_years)
        else:
            # Convert year to int if it's a string, since year_progress keys are integers
            year_key = int(year) if isinstance(year, str) else year
            return self.year_progress.get(year_key, 0.0)

    def get_thumbnail(self):
        # https://secure.syndetics.com/index.aspx?isbn=9780525538424/mc.gif&upc=&client=bcclsvega&type=unbound
        bsurl = "https://images-us.bookshop.org/ingram/{0}.jpg?height=300&v=v2".format(self.isbn13.replace("-", ""))
        olurl = "https://covers.openlibrary.org/b/isbn/{0}-M.jpg".format(self.isbn13)
        gburl = "https://www.googleapis.com/books/v1/volumes?q=isbn:{0}".format(
            self.isbn13.replace("-", "")
        )
        r = requests.get(bsurl)
        if r.status_code == 200 or r.status_code == 403:
            return bsurl
        r = requests.get(olurl)
        if r.status_code == 200:
            return olurl
        gbr = requests.get(gburl)
        if gbr.status_code == 200:
            print(gburl)
            print(gbr.json())
            if (
                gbr.json()["totalItems"] > 0
                and "imageLinks" in gbr.json()["items"][0]["volumeInfo"]
            ):
                return gbr.json()["items"][0]["volumeInfo"]["imageLinks"][
                    "smallThumbnail"
                ]
            else:
                return None

    def print(self, year=None) -> str:
        # Show all years the book was read
        years_str = ', '.join(str(y) for y in self.readYear)
        # Use per-year progress if year is given, else use first
        if year is not None:
            progress = self.get_progress_for_year(year)
        else:
            progress = self.progress[0] if self.progress else 0.0
        return "## ![{0}]({7}) {0}\n*{1}*\n\nRead: {8}\n\n[Massachusetts Library](https://library.minlib.net/search/i={3}) / [Open Library](https://openlibrary.org/isbn/{3}) / [Local Book Shop](https://bookshop.org/book/{3}) / [Amazon](https://amazon.com/dp/{2})\n\n![{5}%](https://geps.dev/progress/{5}) \n\n{6}\n".format(
            self.title,
            " & ".join([a.print_link() for a in self.authors]),
            self.isbn10,
            self.isbn13,
            "-".join(self.title.lower().split()),
            str(round(progress * 100)),
            " ".join([":star:" for i in range(round(self.rating))]),
            self.thumbnail,
            years_str
        )
