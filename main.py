import click
from tabulate import tabulate
from app.models import Department, Employee, Project
from app.models import Base
from app.database import session, engine

# Create tables in the database
Base.metadata.create_all(bind=engine)

@click.group()
def cli():
    pass

def echo_error(message):
    click.secho(message, fg='red')

def echo_success(message):
    click.secho(message, fg='green')

# Adding a Department
@cli.command()
@click.option('--name', prompt='Enter department name')
@click.option('--head_of_dept_id', prompt='Enter head of department ID', type=int)
def add_department(name, head_of_dept_id):
    try:
        if not name:
            raise ValueError("Department name cannot be empty")

        new_department = Department(name=name, head_of_department_id=head_of_dept_id)
        session.add(new_department)
        session.commit()
        echo_success(f"Added department: {name}")
        display_departments()
    except Exception as e:
        echo_error(f"Error adding department: {str(e)}")

# Function to remove a department
@cli.command()
@click.option('--id', prompt='Enter department ID', type=int)
def remove_department(id):
    try:
        department = session.query(Department).filter_by(id=id).first()
        if department:
            session.delete(department)
            session.commit()
            echo_success(f"Removed department with ID: {id}")
            display_departments()
        else:
            echo_error(f"Department with ID {id} not found")
    except Exception as e:
        echo_error(f"Error removing department: {str(e)}")

# Function to display all departments
@cli.command()
def display_departments():
    try:
        departments = session.query(Department).all()
        if departments:
            headers = ["ID", "Name", "Head of Department ID"]
            data = [(department.id, department.name, department.head_of_department_id) for department in departments]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            click.echo("No departments found")
    except Exception as e:
        echo_error(f"Error displaying departments: {str(e)}")

# Function to add an employee
@cli.command()
@click.option('--name', prompt='Enter employee name')
@click.option('--department_id', prompt='Enter department ID', type=int)
def add_employee(name, department_id):
    try:
        if not name:
            raise ValueError("Employee name cannot be empty")

        new_employee = Employee(name=name, department_id=department_id)
        session.add(new_employee)
        session.commit()
        echo_success(f"Added employee: {name}")
        display_employees()
    except Exception as e:
        echo_error(f"Error adding employee: {str(e)}")

# Function to remove an employee
@cli.command()
@click.option('--id', prompt='Enter employee ID', type=int)
def remove_employee(id):
    try:
        employee = session.query(Employee).filter_by(id=id).first()
        if employee:
            session.delete(employee)
            session.commit()
            echo_success(f"Removed employee with ID: {id}")
            display_employees()
        else:
            echo_error(f"Employee with ID {id} not found")
    except Exception as e:
        echo_error(f"Error removing employee: {str(e)}")

# Function to display all employees
@cli.command()
def display_employees():
    try:
        employees = session.query(Employee).all()
        if employees:
            headers = ["ID", "Name", "Department ID"]
            data = [(employee.id, employee.name, employee.department_id) for employee in employees]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            click.echo("No employees found")
    except Exception as e:
        echo_error(f"Error displaying employees: {str(e)}")

# Function to add a project
@cli.command()
@click.option('--name', prompt='Enter project name')
@click.option('--department_id', prompt='Enter department ID', type=int)
def add_project(name, department_id):
    try:
        if not name:
            raise ValueError("Project name cannot be empty")

        new_project = Project(name=name, department_id=department_id)
        session.add(new_project)
        session.commit()
        echo_success(f"Added project: {name}")
        display_projects()
    except Exception as e:
        echo_error(f"Error adding project: {str(e)}")

# Function to remove a project
@cli.command()
@click.option('--id', prompt='Enter project ID', type=int)
def remove_project(id):
    try:
        project = session.query(Project).filter_by(id=id).first()
        if project:
            session.delete(project)
            session.commit()
            echo_success(f"Removed project with ID: {id}")
            display_projects()
        else:
            echo_error(f"Project with ID {id} not found")
    except Exception as e:
        echo_error(f"Error removing project: {str(e)}")

# Function to display all projects
@cli.command()
def display_projects():
    try:
        projects = session.query(Project).all()
        if projects:
            headers = ["ID", "Name", "Department ID"]
            data = [(project.id, project.name, project.department_id) for project in projects]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            click.echo("No projects found")
    except Exception as e:
        echo_error(f"Error displaying projects: {str(e)}")

# Display Head of Departments and Their Departments
@cli.command()
def display_heads_of_departments():
    try:
        heads_of_departments = session.query(Department).filter(Department.head_of_department_id.isnot(None)).all()
        if heads_of_departments:
            headers = ["Head of Department", "Department Name"]
            data = [(head_of_department.head_of_department.name, head_of_department.name) for head_of_department in heads_of_departments]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            click.echo("No head of departments found")
    except Exception as e:
        echo_error(f"Error displaying heads of departments: {str(e)}")

# Display Employees in a Certain Department
@cli.command()
@click.option('--department_name', prompt='Enter department name', type=str)
def display_employees_in_department(department_name):
    try:
        department = session.query(Department).filter_by(name=department_name).first()
        if department:
            employees = department.employees
            if employees:
                headers = ["Employee ID", "Employee Name"]
                data = [(employee.id, employee.name) for employee in employees]
                click.echo(tabulate(data, headers=headers, tablefmt="grid"))
            else:
                echo_success(f"No employees found in Department: {department_name}")
        else:
            echo_error(f"Department: {department_name} not found")
    except Exception as e:
        echo_error(f"Error displaying employees in department: {str(e)}")

# Display Projects Being Worked on by Departments
@cli.command()
def display_projects_by_departments():
    try:
        departments = session.query(Department).all()
        if departments:
            headers = ["Department Name", "Project Name"]
            data = []
            for department in departments:
                for project in department.projects:
                    data.append((department.name, project.name))
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            echo_success("No departments found")
    except Exception as e:
        echo_error(f"Error displaying projects by departments: {str(e)}")
        
if __name__ == '__main__':
    cli()
