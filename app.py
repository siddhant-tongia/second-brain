import mysql.connector
import os 
from dotenv import load_dotenv
load_dotenv()

mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = os.getenv("PASSWORD"),
  database = "second_brain"
)

my_cursor = mydb.cursor()

my_cursor.execute("SELECT * FROM resources")
result = my_cursor.fetchall()

query = "INSERT INTO resources (title, category, short_description, link) VALUES (%s, %s, %s, %s)"
values = (title, category, description, link)

my_cursor.execute(query, values)
mydb.commit()

print(result)