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

title = input("Enter the Title Of Resource:")
category = input("Enter the Category Of Resource:")
description = input("Enter the Description Of Resource:")
link = input("Enter the Link Of Resource:")

query = "INSERT INTO resources (title, category, short_description, link) VALUES (%s, %s, %s, %s)"
values = (title, category, description, link)

my_cursor.execute(query, values)
mydb.commit()


resource_id = input("Enter the ID of the resource to delete: ")

query = "DELETE FROM resources WHERE id = %s"
values = (resource_id,)   # note the comma — why do you think this comma is necessary here?

my_cursor.execute(query, values)
mydb.commit()

my_cursor.execute("SELECT * FROM resources")
result = my_cursor.fetchall()
print(result)