import datetime
from flask import Flask, render_template, g, request, redirect, url_for, flash
import sqlite3

PATH="db/jobs.sqlite"

app = Flask(__name__)
app.secret_key = "my_secret_key"

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
        employer_id, employer_is_new = new_employer_id(employer_name)

        execute_sql(
            "INSERT INTO job (id, title, description, salary, employer_id) VALUES (?, ?, ?, ?, ?)",
            (job_id, title, description, salary, employer_id),
            commit=True
        )

        if employer_is_new:
            execute_sql(
            "INSERT INTO employer (id, name, description, address, city, state, zip) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (employer_id, employer_name, "A job", "123 fake", "Town", "State", "1z3"),
            commit=True
            )

        return redirect("/")
    return render_template("job_post.html")


def new_employer_id(employer_name):
    employers = execute_sql("SELECT DISTINCT id, name FROM employer ORDER BY id")
    for employer in employers:
        if employer[-1] == employer_name:
            return employer[0], False
    return employers[-1][0] + 1, True


def new_job_id():
    query_result = execute_sql("SELECT MAX(id) FROM job")
    return query_result[0][0] + 1

def get_rows(query_result):
    return [val[0] for val in query_result]


@app.route("/delete/<job_id>")
def delete_post(job_id):
    job_title = execute_sql(f"SELECT title FROM job WHERE id = {job_id}")
    execute_sql(f"DELETE FROM job WHERE id = {job_id}", commit=True)
    flash(f"Post {job_title} deleted.", "info")
    return redirect("/")
    
@app.route("/register_employer", methods=("POST", "GET"))
def register_employer():
    if request.method == "POST":
        employer_name = request.form["employer_name"]
        description = request.form["description"]
        address = request.form["address"]
        city = request.form["city"]
        state = request.form["state"]
        zip_code = request.form["zip"]

        employer_id, employer_is_new = new_employer_id(employer_name)

        if employer_is_new:
            execute_sql(
                "INSERT INTO employer (id, name, description, address, city, state, zip) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (employer_id, employer_name, description, address, city, state, zip_code),
                commit=True
                )
            return redirect("/")
            
        if not employer_is_new:
            flash(f"Employer {employer_name} already exists.", "info")
            return redirect("/")
    return render_template("register_employer.html")