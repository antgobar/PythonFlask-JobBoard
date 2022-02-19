import datetime
from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3

PATH="db/jobs.sqlite"

app = Flask(__name__)

def open_connection():
    connection = getattr(g, "_connection", None)
    if connection is None:
        connection = g._connection  = sqlite3.connect(PATH)
    connection.row_factory = sqlite3.Row
    return connection

def execute_sql(sql, values=(), commit=False, single=False):
    connection = open_connection()
    cursor = connection.execute(sql, values)
    if commit == True:
        results = connection.commit()
    else:
        results = cursor.fetchone() if single else cursor.fetchall()
    cursor.close()
    return results

@app.teardown_appcontext
def close_connection(exception):
    connection = getattr(g, "_connection", None)
    if connection is not None:
        connection.close()

@app.route("/")
@app.route("/jobs")
def jobs():
    jobs = execute_sql(
        "SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id"
        )
    return render_template("index.html", jobs=jobs)

@app.route("/job/<job_id>")
def  job(job_id):
    job = execute_sql(
        "SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id WHERE job.id = ?", 
        [job_id],
        single=True
        )
    return render_template("job.html", job=job)

@app.route("/employer/<employer_id>")
def employer(employer_id):
    employer = execute_sql(
        "SELECT * FROM employer WHERE id=?",
        [employer_id],
        single=True
    )
    jobs = execute_sql(
        "SELECT job.id, job.title, job.description, job.salary FROM job JOIN employer ON employer.id = job.employer_id WHERE employer.id = ?",
        [employer_id]
    )
    reviews= execute_sql(
        "SELECT review, rating, title, date, status FROM review JOIN employer ON employer.id = review.employer_id WHERE employer.id = ?",
        [employer_id]
    )
    return render_template(
        "employer.html", 
        employer=employer, 
        jobs=jobs,
        reviews=reviews)

@app.route("/employer/<employer_id>/review", methods=("GET", "POST"))
def review(employer_id):
    if request.method == "POST":
        review = request.form["review"]
        rating = request.form["rating"]
        title = request.form["title"]
        status = request.form["status"]
        
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        execute_sql(
            "INSERT INTO review (review, rating, title, date, status, employer_id) VALUES (?, ?, ?, ?, ?, ?)",
            (review, rating, title, date, status, employer_id),
            commit=True
        )
        
        return redirect(url_for("employer", employer_id=employer_id))
    return render_template("review.html", employer_id=employer_id)

@app.route("/job_post", methods=("POST", "GET"))
def job_post():
    if request.method == "POST":
        employer_name = request.form["employer_name"]
        title = request.form["title"]
        salary = request.form["salary"]
        description = request.form["description"]
        job_id = new_job_id()
        employer_id = new_employer_id(employer_name)

        execute_sql(
            "INSERT INTO job (employer_name, title, salary, description) VALUES (?, ?, ?, ?)",
            (employer_name, title, salary, description),
            commit=True
        )
        return redirect("/")
    return render_template("job_post.html")


def new_employer_id(employer_name):
    query_result = execute_sql("SELECT DISTINCT employer_id, name FROM job JOIN employer ON employer.id = job.employer_id")
    query_dict = {val[-1]: val[0] for val in query_result}
    for key in query_dict:
        if key == employer_name:
            return query_dict[key]
    return max(query_dict.values()) + 1

def new_job_id():
    query_result = execute_sql("SELECT MAX(id) FROM job")
    return query_result[0][0] + 1

def get_rows(query_result):
    return [val[0] for val in query_result]


if __name__ == "__main__":
    new_employer_id()