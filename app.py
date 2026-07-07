import mysql.connector
import os 
from dotenv import load_dotenv
load_dotenv()

def insert(title, category, description, link):
  query = "INSERT INTO resources (title, category, short_description, link) VALUES (%s, %s, %s, %s)"
  values = (title, category, description, link)

  my_cursor.execute(query, values)
  mydb.commit()

def delete_multiple(id_list):
  placeholder = ", ".join(["%s"] * len(id_list))
  query = f"DELETE FROM resources WHERE id IN ({placeholder})"

  my_cursor.execute(query, tuple(id_list))
  mydb.commit()

def view_all():
  my_cursor.execute("SELECT * FROM resources")
  result = my_cursor.fetchall()

  col = ("ID", "Title", "Category", "Description", "Link", "Created_at", "Updated_at")

  for row in result:
    for label, value in zip(col, row):
      print(f"{label}: {value}")
    print("---")

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

insert(title, category, description, link)

resource_ids = input("Enter the ID of the resource to delete(seperated by commas{,}): ")
id_list = [int(x) for x in resource_ids.split(",")]

delete_multiple(id_list)

view_all()