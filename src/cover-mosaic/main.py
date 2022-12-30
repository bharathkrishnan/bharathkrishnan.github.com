import functions_framework
import requests
from PIL import Image
from io import BytesIO
from flask import send_file


def get_thumbnail(ids):
    imgs = []
    print(ids)
    for id in ids:
        olurl = "https://covers.openlibrary.org/b/isbn/{0}-M.jpg".format(id)
        gburl = "https://www.googleapis.com/books/v1/volumes?q=isbn:{0}".format(
            id.replace("-", "")
        )
        r = requests.get(olurl)
        if r.status_code == 200:
            imgs.append(olurl)
        else:
            gbr = requests.get(gburl)
            if gbr.status_code == 200:
                if (
                    gbr.json()["totalItems"] > 0
                    and "imageLinks" in gbr.json()["items"][0]["volumeInfo"]
                ):
                    imgs.append(
                        gbr.json()["items"][0]["volumeInfo"]["imageLinks"][
                            "smallThumbnail"
                        ]
                    )
    return imgs


@functions_framework.http
def cover_mosaic(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    print(request)
    if request_json and "ids" in request_json:
        ids = request_json["ids"]
    elif request_args and "ids" in request_args:
        ids = request_args["ids"]
    else:
        ids = request.form.get("ids").split(",")
    if len(ids) == 0:
        return "Hmm.. no books to be found here"
    imgs = get_thumbnail(ids)
    bw = 200
    images = []
    for i in imgs:
        raw_img = Image.open(requests.get(i, stream=True).raw)
        raw_img = raw_img.resize(
            (bw, int(float(raw_img.height) / float(raw_img.width) * bw))
        )
        images.append(raw_img)

    mh = 1 if len(images) < 5 else int(len(images) / 5) + 1
    mw = len(images) if len(images) < 5 else 5

    mosaic = Image.new("RGB", (mw * bw, mh * images[0].height))

    row = 0
    col = 0
    print("Num images: {0}".format(len(images)))
    for i in images:
        print(row, col, (col * bw, row * i.height))
        mosaic.paste(i, (col * bw, row * i.height))
        row = row + 1 if col == 4 else row
        col = 0 if col == 4 else col + 1

    img_io = BytesIO()
    mosaic.save(img_io, "JPEG", quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype="image/jpeg", as_attachment=True, download_name='cover_mosaic.jpg')
