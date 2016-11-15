from os import listdir
from os import path
import requests
import json
import re
from flask import Flask
from flask import request
from flask import render_template
from flask import url_for

api_place = "https://en.wikipedia.org/w/api.php"
static_directory = "/static"
app = Flask(__name__, static_url_path=static_directory)


class PosterPage :
    def __init__(self, page):
        info = page.get("imageinfo")[0]
        self.url = info.get("url")
        self.file_type = info.get("mediatype")
        self.title, self.ext = path.splitext(page.get("title"))
        self.title = self.title[len("file:"):]

    def __repr__(self):
        return str({ "url": self.url, "title": self.title })


def main():
    app.run(debug=True)

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    posters = []

    if query is not None:
        posters = find_movie_poster_url(query)

    return render_template("search.html", posters=posters, query=query)

@app.route("/")
def main_page():
    return render_template("main.html")

def find_movie_poster_url(name):
    data = { "action": "query",
             "generator": "search",
             "prop": "imageinfo",
             "iiprop": "url|mediatype",
             "gsrenablerewrites": False,
             "gsearch": "nearmatch",
             "gsrnamespace": 6,
             "gsrsearch": str.join(" ",["file:", "poster", name]),
             "format": "json" }

    result = requests.get(api_place, data)
    pages = json.loads(result.text)

    posters = map(PosterPage, pages.get("query").get("pages").values())
    posters = filter(lambda p: p.file_type == "BITMAP", posters)

    return list(posters)

@app.route("/list/")
def list_posters():
    images = map(lambda img: url_for("static", filename=img),
                 listdir("."+static_directory))

    return render_template("list.html", images = images)

if __name__ == "__main__":
    main()
