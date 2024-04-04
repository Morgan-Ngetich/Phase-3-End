# Project Title

Employee Management System

## Project Description

The Employee Management System is a command-line application designed to manage departments, employees, and projects within an organization. It allows users to perform various operations such as adding and removing departments, employees, and projects, as well as assigning employees to departments and projects.

## Table of Contents

1. [How the Project Works](#how-the-project-works)
2. [How to Use the Project](#how-to-use-the-project)
3. [Features](#features)
4. [Built With](#built-with)
5. [Authors](#authors)
6. [License](#license)


## How the Project Works

The Employee Management System follows a client-server architecture. It consists of a Python backend that handles database operations and a command-line interface (CLI) that serves as the frontend for user interactions.

### Backend

The backend of the Employee Management System is built using Python and relies on the SQLAlchemy library to interact with the SQLite database. It defines models for departments, employees, and projects, and establishes relationships between them. The backend handles CRUD (Create, Read, Update, Delete) operations on the database, ensuring data integrity and consistency.

### Command-Line Interface (CLI)

The CLI is the primary interface for users to interact with the Employee Management System. It is implemented using the Click library, which provides a framework for building command-line applications in Python. The CLI offers a set of commands that users can execute to perform various tasks such as adding or removing departments, employees, and projects, as well as assigning employees to departments and projects.

### Database

The Employee Management System uses SQLite as its backend database. SQLite is a lightweight and self-contained database engine that does not require a separate server process. This makes it well-suited for embedded systems and small to medium-sized applications like this one. The database stores information about departments, employees, and projects, maintaining relationships between them to reflect the organizational structure accurately.

### Workflow

When a user interacts with the CLI, commands are executed that trigger corresponding actions in the backend. For example, when the user adds a new employee to a department, the CLI sends a request to the backend to create a new employee entity and associate it with the specified department in the database. Similarly, when the user requests to view employee information, the CLI retrieves the relevant data from the database and presents it to the user in a readable format.

Overall, the Employee Management System provides a seamless and efficient way for organizations to manage their workforce and project assignments through a user-friendly command-line interface backed by a robust database backend.


## Installation
1. Clone the repository:
```
git@github.com:Morgan-Ngetich/Phase-3-End.git
```

2. Install dependencies 
```
pip install -r requirements.txt
```

3. Run the Program:
 ```
 python main.py
 ```

4. Ensure you have Python installed.

5.  Use the available commands to perform operations such as adding departments, employees, and projects, removing entities, assigning employees to departments and projects, and viewing employee information.


## Features

- Add, remove, and display departments.
- Add, remove, and display employees.
- Add, remove, and display projects.
- Assign employees to departments.
- Assign projects to employees.
- View employee information.

## Built With

- Python
- SQLAlchemy
- Click
- SQLite

## Authors

- [Morgan-Ngetich](https://github.com/Morgan-Ngetich)

## License

This project is licensed under the [MIT]() License.
