"""
This script is a data querying application for a student database. It allows users to perform
various queries such as viewing subjects taken by a student, looking up addresses, listing
reviews, courses taught by teachers, and identifying students based on course completion
and grades. The application interacts with an SQLite database and provides options to store
query results in JSON or XML formats.
"""

# Import the required modules:
import sqlite3
import xml.etree.ElementTree as ET
import json

# Connect to the database:
try:
    conn = sqlite3.connect("HyperionDev.db")
except sqlite3.Error:
    print("Please store your database as HyperionDev.db")
    quit()

cur = conn.cursor()


# Check if the given ID is valid (13 alphanumeric characters).
def is_valid_id(id_str):
    return len(id_str) == 13 and id_str.isalnum()


# Check if the number of arguments provided is correct.
def usage_is_incorrect(input_list, num_args):
    if len(input_list) != num_args + 1:
        print(f"The {input_list[0]} command requires {num_args} arguments.")
        return True
    return False


# Store the given data as a JSON file.
def store_data_as_json(data, filename):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nThe results have been saved to {filename}\n")
    except IOError as e:
        print(f"\nError saving JSON to file {e}\n")    


# Store the given data as a XML file.
def store_data_as_xml(data, filename):
    try:
        root = ET.Element("results")
        for row in data:
            item = ET.SubElement(root, "item")
            for i, value in enumerate(row):
                ET.SubElement(item, f"field_{i}").text = str(value)

        tree = ET.ElementTree(root)
        tree.write(filename)
        print(f"\nThe results have been saved to {filename}\n")
    except IOError as e:
        print(f"\nError saving the XML file: {e}\n")


# Offer the user to store the query results and handle the storage process.
def offer_to_store(data):
    while True:
        print("\nWould you like to store this result?\n")
        choice = input("Y/[N]? : ").strip().lower()

        if choice == "y":
            filename = input("Specify filename. Must end in .xml or .json: ")
            ext = filename.split(".")[-1]
            if ext == 'xml':
                store_data_as_xml(data, filename)
            elif ext == 'json':
                store_data_as_json(data, filename)
            else:
                print("\nInvalid file extension. Please use .xml or .json\n")

        elif choice == 'n':
            break

        else:
            print("\nInvalid choice\n")


# Define the usage instructions.
def execute_query(query, params=None):
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()
    except sqlite3.Error as e:
        print(f"\nThere has been a database error: {e}\n")
        return None


# Define the usage instructions:
usage = '''
What would you like to do?

d - demo
vs <student_id>            - view subjects taken by a student
la <firstname> <surname>   - lookup address for a given firstname and surname
lr <student_id>            - list reviews for a given student_id
lc <teacher_id>            - list all courses taught by teacher_id
lnc                        - list all students who haven't completed their course
lf                         - list all students who have completed their course and achieved 30 or below
e                          - exit this program

Type your option here: '''

print("Welcome to the data querying app!")

valid_commands = {'d', 'vs', 'la', 'lr', 'lc', 'lnc', 'lf', 'e'}

# This is the main loop:
while True:

    print()
    # Get input from user:
    user_input = input(usage).strip().lower()

    # Check for exit command before splitting:
    if user_input == 'e':
        print("\nProgram exited successfully!\n")
        break
    user_input = user_input.split()
    print()

    # Parse user input into command and args:
    if not user_input:
        print("\nError: No command entered. Please try again.\n")
        continue

    command = user_input[0]
    args = user_input[1:] if len(user_input) > 1 else []

    if command not in valid_commands:
        print(f"\nError: '{command}' is not a valid command. Please try again.\n")
        continue

    # This prints all student names and surnames:
    if command == 'd': 
        data = cur.execute("SELECT * FROM Student")
        for _, firstname, surname, _, _ in data:
            print(f"{firstname} {surname}")

    # view subjects by student_id:    
    elif command == 'vs': 
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        query = """
            SELECT DISTINCT c.course_name
            FROM Student s
            JOIN StudentCourse sc ON s.student_id = sc.student_id
            JOIN Course c ON sc.course_code = c.course_code
            WHERE s.student_id = UPPER(?)
        """
        data = execute_query(query, (student_id,))
        if data:
            for row in data:
                print(f"Subject: {row[0]}")
            offer_to_store(data)
        else:
            print("No subjects were found for this student ID.")

    # list address by name and surname:
    elif command == 'la': 
        if usage_is_incorrect(user_input, 2):
            continue
        firstname, lastname = args[0].strip().capitalize(), args[1].strip().capitalize()
        if not firstname.isalpha() or not lastname.isalpha():
            print("\nError: First name and surname should only contain alphabetic characters.\n")
            continue
        query = """
            SELECT a.street, a.city
            FROM Student s
            JOIN Address a ON s.address_id = a.address_id
            WHERE s.first_name = ? AND last_name = ?
        """
        data = execute_query(query, (firstname, lastname))
        if data:
            for row in data:
                print(f"Address: {row[0]}, {row[1]}")
            offer_to_store(data)
        else:
            print("\nNo address found for this name.\n")
    
    # list reviews by student_id:
    elif command == 'lr':
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]
        query = """
            SELECT completeness, efficiency, style, documentation, review_text
            FROM Review
            WHERE student_id = UPPER(?)
        """
        data = execute_query(query, (student_id,))
        if data:
            for row in data:
                print(f"Completeness: {row[0]}, Efficiency: {row[1]}, Style: {row[2]}, Documentation: {row[3]}")
                print(f"Review: {row[4]}\n")
            offer_to_store(data)
        else:
            print("\nNo reviews were found for this student ID.\n")
    
    # list courses by teacher_id:
    elif command == 'lc':
        if usage_is_incorrect(user_input, 1):
            continue
        teacher_id = args[0]
        query = """
        SELECT DISTINCT c.course_name
        FROM Teacher t
        JOIN Course c ON t.teacher_id = c.teacher_id
        WHERE t.teacher_id = UPPER(?)
    """
        data = execute_query(query, (teacher_id,))
        if data:
            print(f"Courses taught by teacher ID {teacher_id}:")
            for row in data:
                print(f"Course: {row[0]}")
            offer_to_store(data)
        else:
            print(f"\nNo courses found for teacher ID {teacher_id}.\n")
    
    # list all students who haven't completed their course:
    elif command == 'lnc':
        query = """
            SELECT s.student_id, s.first_name, s.last_name, s.email, c.course_name
            FROM Student s
            JOIN StudentCourse sc ON s.student_id = sc.student_id
            JOIN Course c ON sc.course_code = c.course_code
            WHERE sc.is_complete = 0
        """
        data = execute_query(query)
        if data:
            for row in data:
                print(f"Student ID: {row[0]}, Name: {row[1]} {row[2]}, Email: {row[3]}, Course: {row[4]}")
            offer_to_store(data)
        else:
            print("\nNo students with incomplete courses were found.\n")

    # list all students who have completed their course and got a mark <= 30
    elif command == 'lf':
        query = """
            SELECT s.student_id, s.first_name, s.last_name, s.email, c.course_name, sc.mark
            FROM Student s
            JOIN StudentCourse sc ON s.student_id = sc.student_id
            JOIN Course c ON sc.course_code = c.course_code
            WHERE sc.is_complete = 1 AND sc.mark <= 30
        """
        data = execute_query(query)
        if data:
            for row in data:
                print(f"Student ID: {row[0]}, Name: {row[1]} {row[2]}, Email: {row[3]}, Course: {row[4]}, Mark: {row[5]}")
            offer_to_store(data)
        else:
            print("\nNo students with completed courses and low scores found.\n")

    else:
        print(f"\nIncorrect command: '{command}'\n")

# Close the database connection
conn.close()
