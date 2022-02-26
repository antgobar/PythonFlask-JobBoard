import sqlite3
import pandas

def main():
    PATH="db/jobs.sqlite"
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM job WHERE id = 14")
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    print(result)

if __name__ == "__main__":
    main()