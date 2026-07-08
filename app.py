import mysql.connector
import os
import sys 
from openai import OpenAI
import requests
import json
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

def prompt(resource_text,user_question):
  return f'''
  You are the retrieval engine for a personal "Second Brain" knowledge system. Your task is to analyze a list of saved resources and identify which ones are conceptually relevant to the user's query.

  Each resource in the dataset contains four fields: "ID", "Title", "Category", and "Description".

  Retrieval Rules:

  Match based on underlying concepts and intent, not just exact keywords.

  If you find relevant resources, add their exact IDs to the matching_ids list and leave the message field empty.

  If no resources match the query, leave the matching_ids list empty and provide a polite, well-written response in the message field stating that no relevant notes were found in the archive.

  Saved Resources:
  {resource_text}

  User Query:
  {user_question}

  Output Constraints:
  You must output your response as raw, valid JSON.

  Do not include any explanations, greetings, or conversational text outside the JSON object.

  Do not wrap the JSON in Markdown formatting or code blocks (e.g., do not use ```json).

  Use this exact schema:
  {{"matching_ids": [list of integers], "message": "String or null"}}'''

def call_ai(prompt_text):
  try:
      client = OpenAI(
      api_key=os.getenv("API_KEY"),
      base_url="https://openrouter.ai/api/v1",
      )
      response = client.chat.completions.create(
          model="tencent/hy3:free",
          messages=[{"role": "user", "content": prompt_text}],
      )
      return response.choices[0].message.content
  
  except Exception as e:
      print(f"Error generating:{e}")
      return None  

def extraction(matching_id):
  ids = ", ".join(["%s"] * len(matching_id))
  query = f"SELECT * FROM resources WHERE id IN ({ids})"

  my_cursor.execute(query,tuple(matching_id))
  return my_cursor.fetchall()

def ai_search(user_question):
  my_cursor.execute("SELECT id, title, category, short_description FROM resources")
  result = my_cursor.fetchall()

  resource_text = ""

  col = ("ID", "Title", "Category", "Description")
  for row in result:
    resource_text += ", ".join(f"{label}: {value}" for label, value in zip(col, row)) + "\n"
    pass

  prompt_text = prompt(resource_text, user_question)
  response = call_ai(prompt_text)
  if response is None:
    print("Sorry, the AI search couldn't be completed right now. Please try again later.")
    return
  else:
    data = json.loads(response)
    matching_ids = data["matching_ids"]
    message = data["message"]

    if(matching_ids):
      result = extraction(matching_ids)
      display_results(result)
      pass
    else:
      print(message)



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
    user_question = input("Hey I am your second brain helper to extract useful resources, today how may i help you:\n")
    ai_search(user_question)
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



  
