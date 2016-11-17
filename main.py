from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from os import listdir
from os import path
import json
import re
import requests
import sys

api_place = "https://en.wikipedia.org/w/api.php"
static_directory = "/static"
app = Flask(__name__, static_url_path=static_directory)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class PosterPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, unique=True)
    file_type = db.Column(db.String)
    title = db.Column(db.String)
    ext = db.Column(db.String)
    picked = db.Column(db.Boolean)

    def full_path():
        return title + ext

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

@app.route("/pick", methods=["POST"])
def pick():
    poster_id = request.form.get("poster_id")
    poster = PosterPage.query.filter_by(id=poster_id).first()
    result = json.dumps({ "success": False }), 400, { "ContentType": "application/json" }

    if poster is not None:
        poster.picked = not poster.picked
        db.session.commit()
        result = json.dumps({ "success": True }), 200, { "ContentType": "application/json" }

    return result

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    posters = []

    if query is not None:
        posters = find_movie_poster_url(query)

    for poster in posters:
        db_poster = PosterPage.query.filter_by(url=poster.url).first()
        if db_poster is None:
            db.session.add(poster)
            db_poster = poster
        db_posters.append(db_poster)

    db.session.commit()

    return render_template("search.html", posters=db_posters, query=query)
    db_posters = []
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
    images = PosterPage.query.filter_by(picked=True)
    # images = map(lambda img: url_for("static", filename=img),
    #              listdir("."+static_directory))

    return render_template("list.html", images = images)

if __name__ == "__main__":
    main()
    if sys.argv[0] == "create_db":
        db.create_all()
