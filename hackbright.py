"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    print("Student: {} {}\nGitHub account: {}".format(row[0], row[1], row[2]))


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """

    QUERY = """
        INSERT INTO students (first_name, last_name, github)
        VALUES (:first_name, :last_name, :github)
    """

    db.session.execute(QUERY, {
        'first_name' : first_name,
        'last_name' : last_name,
        'github' : github
        })
    print('Data has been inserted succesfully!')
    db.session.commit()
    


def get_project_by_title(title):
    """Given a project title, print information about the project."""
    
    QUERY = """
        SELECT title, description, max_grade
        FROM projects
        WHERE title = :title
    """
    cursor = db.session.execute(QUERY, {'title' : title})

    row = cursor.fetchone()

    # print(f"Project name: {row[0]} \n Description: {row[1]} \n Maximum grade: {row[2]}")
    return row

def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    
    QUERY = """
        SELECT grade
        FROM grades
        WHERE student_github = :student_github AND project_title = :project_title
    """

    cursor = db.session.execute(QUERY, {'student_github':github, 'project_title':title})
    row = cursor.fetchone()

    #student's grade does NOT exist
    if row is None:
        print("This student does not have a grade yet. Please insert a grade using the 'grade' command.")
    else:
        #student's grade exists!
        print(f"Grades is {row[0]} for {title}")



def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    QUERY = """
    INSERT INTO grades(student_github, project_title, grade)
        VALUES(:github, :title, :grade)
    """

    db.session.execute(QUERY, {'github':github, 'title': title, 'grade': grade})
    db.session.commit()

    print(f"{github}'s project {title}'s grade is {grade} and has succesfully been insterted!")

#user adds new project!
def add_project(title, description, max_grade):
    """User can add new projects to projects table."""

    QUERY = """
    INSERT INTO projects(title, description, max_grade)
        VALUES(:title, :description, :max_grade)
    """

    db.session.execute(QUERY, {'title':title, 'description':description, 'max_grade':max_grade})
    db.session.commit()

    #checking if user's new project has been successfully inserted
    #title args below is the user's input
    if get_project_by_title(title) is None:
        print("Your project was not successfully inserted. Please try again!")
    else:
        print("Congratulations! Your project was successfully inserted!")


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "projects":
            title = args[0]
            get_project_by_title(title)

        elif command == "grade":
            github, title = args
            get_grade_by_github_title(github, title)

        elif command == "give_grade":
            github, title, grade = args
            assign_grade(github, title, grade)

        elif command == "new_project":
            title, description, max_grade = args[0], args[1:-1], args[-1]
            str_description = " ".join(description)
            add_project(title, str_description, max_grade)


        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
