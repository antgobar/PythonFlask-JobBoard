import sqlite3
import pandas

def main():
    PATH="db/jobs.sqlite"
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    employer_name = "Sharp Group"
    cursor.execute("SELECT MAX(id) FROM job")
    result = cursor.fetchall()
    print(result)


def get_rows(query_result):
    return [val[0] for val in query_result]

if __name__ == "__main__":
    main()