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


def view_by_category(selected_category):
  query = "SELECT * FROM resources WHERE Category = %s"
  values = (selected_category,)
  
  my_cursor.execute(query,values)
  result = my_cursor.fetchall()
  display_results(result)

def display_results(result):
  col = ("ID", "Title", "Category", "Description", "Link", "Created_at", "Updated_at")

  for row in result:
    for label, value in zip(col, row):
      print(f"{label}: {value}")
    print("---")
def view_all():
  my_cursor.execute("SELECT * FROM resources")
  result = my_cursor.fetchall()
  display_results(result)


mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = os.getenv("PASSWORD"),
  database = "second_brain"
)

my_cursor = mydb.cursor()

while True:
  print("1. Add Resource")
  print("2. Search by AI")
  print("3. Browse by Category")
  print("4. Delete Resource")
  print("5. Exit")

  option = int(input("Enter the choice (1 to 5): "))
  if(option == 1):
    title = input("Enter the Title Of Resource:")
    category = input("Enter the Category Of Resource:")
    description = input("Enter the Description Of Resource:")
    link = input("Enter the Link Of Resource:")

    insert(title, category, description, link)
    pass

  elif(option == 2):
    print("coming soon!")
    pass

  elif(option == 3):
    categories = ["AI Resources", "Business Ideas", "DSA Concepts", "Motivation", "Personal Growth"]

    for i,cat in enumerate (categories,start = 1):
      print(f"{i}: {cat}")  

    choice = (input("Choose a categories (1-5) and if want to view all categories then type all :")).lower()

    if(choice != "all"):
      id_list = [int(num) for num in choice.split(",")]

      for i in id_list:
        selected_category = categories[i-1]
        view_by_category(selected_category);

    else:
      view_all()

    pass
  elif(option == 4):
    resource_ids = input("Enter the ID of the resource to delete(seperated by commas{,}): ")
    id_list = [int(x) for x in resource_ids.split(",")]

    delete_multiple(id_list)
    pass

  elif(option == 5):
    break

  else:
    print("Invalid choice, try again")

