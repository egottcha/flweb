from flask import Flask, render_template, flash
from content_management import Content

TOPIC_DICT = Content()

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template("main.html")


@app.route('/dashboard/')
def dashboard():
    flash("flash test!!!!")
    flash("fladfasdfsaassh test!!!!")
    flash("asdfas asfsafs!!!!")
    return render_template("dashboard.html", TOPIC_DICT=TOPIC_DICT)


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    return render_template("login.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", error=e)


if __name__ == "__main__":
    app.secret_key = '12345'

    app.debug = True
    app.run()
