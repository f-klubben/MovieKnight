from os import path
import requests
import json
import re
from flask import Flask
from flask import request
from flask import render_template

api_place = "https://en.wikipedia.org/w/api.php"
app = Flask(__name__)

def main():
    # result = find_movie_poster_url("die hard 2")

    # for r in result:
    #     print(json.dumps(r.__dict__, indent=2))
    app.run(debug=True)

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    posters = []

    if query is not None:
        posters = find_movie_poster_url(query)

    return render_template("search.html", posters=posters, query=query)

@app.route("/")
def hello():
    return render_template("main.html")


class PosterPage :
    def __init__(self, page):
        info = page.get("imageinfo")[0]
        self.url = info.get("url")
        self.file_type = info.get("mediatype")
        self.title, self.ext = path.splitext(page.get("title"))
        self.title = self.title[len("file:"):]

    def __repr__(self):
        return str({ "url": self.url, "title": self.title })


def find_movie_poster_url(name):
    data = { "action": "query",
             "generator": "search",
             "prop": "imageinfo",
             "iiprop": "url|mediatype",
             "gsrenablerewrites": False,
             "gsrnamespace": 6,
             "gsrsearch": str.join(" ",["file:", "poster", name]),
             "format": "json" }

    result = requests.get(api_place, data)
    pages = json.loads(result.text)

    posters = map(PosterPage, pages.get("query").get("pages").values())
    posters = filter(lambda p: p.file_type == "BITMAP", posters)

    return list(posters)

if __name__ == "__main__":
    main()
