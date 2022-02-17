from flask import Flask, render_template

app = Flask(__name__)


@route("/jobs")
@route("/")
def jobs():
    return render_template("index.html")