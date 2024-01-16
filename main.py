import click
from tabulate import tabulate
from app.models import Department, Employee, Project
from app.models import Base
from app.database import session, engine
from sqlalchemy.exc import IntegrityError

# Create tables in the database
Base.metadata.create_all(bind=engine)

def echo_error(message):
    click.secho(message, fg='red')

def echo_success(message):
    click.secho(message, fg='green')

def validate_name(ctx, param, value):
    if not value:
        raise click.BadParameter('Name cannot be empty.')
    return value

# Updated add_entity function
def add_entity(entity, name, **kwargs):
    try:
        new_entity = entity(name=name, **kwargs)
        session.add(new_entity)
        session.commit()
        echo_success(f"Added {entity.__name__.lower()}: {name}")
        display_entities(entity)
        return new_entity  # Return the newly added entity
    except IntegrityError as ie:
        session.rollback()  # Rollback the session to avoid leaving the transaction open
        echo_error(f"IntegrityError: {str(ie)}")
        echo_error(f"{entity.__name__.lower()} with name '{name}' already exists. Please choose a different name.")
        return None  # Return None on IntegrityError
    except Exception as e:
        session.rollback()  # Rollback the session in case of other exceptions
        echo_error(f"Error adding {entity.__name__.lower()}: {str(e)}")
        return None  # Return None on other exceptions

# Remove Entity Function
def remove_entity(entity, name, prompt_id=False):
    try:
        if prompt_id:
            entity_id = click.prompt(f'Enter the ID of the {entity.__name__.lower()} to remove', type=int)
            entity_instance = session.query(entity).filter_by(id=entity_id).first()
        else:
            entity_instance = session.query(entity).filter_by(name=name).first()

        if entity_instance:
            session.delete(entity_instance)
            session.commit()
            echo_success(f"Removed {entity.__name__.lower()}: {entity_instance.name}")
            display_entities(entity)
        else:
            echo_error(f"{entity.__name__.lower()} with name '{name}' not found")
    except Exception as e:
        echo_error(f"Error removing {entity.__name__.lower()}: {str(e)}")

def display_entities(entity):
    try:
        entities = session.query(entity).all()
        if entities:
            headers = ["ID", "Name"]
            data = [(entity_instance.id, entity_instance.name) for entity_instance in entities]
            click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
        else:
            click.echo(f"No {entity.__name__.lower()}s found")
    except Exception as e:
        echo_error(f"Error displaying {entity.__name__.lower()}s: {str(e)}")

def get_available_employees():
    return session.query(Employee).filter(Employee.department_id.is_(None)).all()

def add_employees_to_department(department):
    try:
        available_employees = get_available_employees()

        if not available_employees:
            echo_error("No available employees to add to the department.")
            return

        headers = ["ID", "Name"]
        data = [(employee.id, employee.name) for employee in available_employees]
        click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))

        # Prompt user to select employees to add to the department
        employee_ids = click.prompt('Enter the IDs of the employees to add (comma-separated)', type=str)
        employee_ids = [int(e_id) for e_id in employee_ids.split(',') if e_id.isdigit()]

        # Select head of department
        head_of_dept_id = click.prompt('Choose an employee ID to be the head of the department', type=int)
        head_of_dept = session.query(Employee).filter_by(id=head_of_dept_id).first()

        if not head_of_dept:
            echo_error(f"Employee with ID {head_of_dept_id} not found.")
            return

        # Add head of department
        department.head_of_department = head_of_dept
        session.commit()

        for employee_id in employee_ids:
            employee = session.query(Employee).filter_by(id=employee_id).first()
            if employee:
                employee.department_id = department.id
            else:
                echo_error(f"Employee with ID {employee_id} not found.")

        echo_success(f"Employees added to department {department.name}")
    except Exception as e:
        echo_error(f"Error adding employees to department: {str(e)}")

@click.group()
def cli():
    pass

# Adding a Department
@cli.command()
@click.option('--name', prompt='Enter department name', callback=validate_name)
def add_department(name):
    try:
        existing_department = session.query(Department).filter_by(name=name).first()
        if existing_department:
            echo_error(f"Department with name '{name}' already exists. Please choose a different name.")
        else:
            new_department = add_entity(Department, name)
            if new_department:
                add_employees_to_department(new_department)
    except Exception as e:
        echo_error(f"Error adding department: {str(e)}")

# Removing a Department
@cli.command()
@click.option('--name', prompt='Enter department name', callback=validate_name)
def remove_department(name):
    remove_entity(Department, name)

# Displaying Departments
@cli.command()
def display_departments():
    display_entities(Department)

# Adding an Employee
@cli.command()
@click.option('--name', prompt='Enter employee name', callback=validate_name)
def add_employee(name):
    try:
        departments = session.query(Department).all()

        if not departments:
            echo_error("No available departments to assign the employee to.")
            add_entity(Employee, name)  # Add the employee without assigning to any department
        else:
            headers = ["ID", "Name"]
            data = [(department.id, department.name) for department in departments]
            click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))

            add_to_department = click.confirm('Do you want to add the employee to a department?', default=True)

            if add_to_department:
                department_name = click.prompt('Choose a department name to assign the employee to', type=str)

                department = session.query(Department).filter_by(name=department_name).first()
                if department:
                    add_entity(Employee, name, department_id=department.id)
                else:
                    echo_error(f"Department '{department_name}' not found.")
            else:
                add_entity(Employee, name)  # Add the employee without assigning to any department

    except Exception as e:
        echo_error(f"Error adding employee: {str(e)}")

# Removing an Employee
@cli.command()
@click.option('--name', prompt='Enter employee name', callback=validate_name)
def remove_employee(name):
    remove_entity(Employee, name, prompt_id=True)

# Displaying Employees
@cli.command()
def display_employees():
    display_entities(Employee)

# Adding a Project
@cli.command()
@click.option('--name', prompt='Enter project name', callback=validate_name)
def add_project(name):
    try:
        departments = session.query(Department).all()
        if departments:
            headers = ["ID", "Name"]
            data = [(department.id, department.name) for department in departments]
            click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
            department_name = click.prompt('Choose a department name to assign the project to', type=str)
            
            department = session.query(Department).filter_by(name=department_name).first()
            if department:
                add_entity(Project, name, department_id=department.id)
            else:
                echo_error(f"Department '{department_name}' not found.")
        else:
            echo_error("No departments found. Please add a department first.")
    except Exception as e:
        echo_error(f"Error adding project: {str(e)}")

# Removing a Project
@cli.command()
@click.option('--name', prompt='Enter project name', callback=validate_name)
def remove_project(name):
    remove_entity(Project, name, prompt_id=True)

# Displaying Projects
@cli.command()
def display_projects():
    display_entities(Project)

# Displaying Head of Departments and Their Departments
@cli.command()
def display_heads_of_departments():
    try:
        heads_of_departments = session.query(Department).filter(Department.head_of_department_id.isnot(None)).all()
        if heads_of_departments:
            headers = ["Head of Department", "Department Name"]
            data = [(head_of_department.head_of_department.name if head_of_department.head_of_department else None, head_of_department.name) for head_of_department in heads_of_departments]
            click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
        else:
            click.echo("No head of departments found")
    except Exception as e:
        echo_error(f"Error displaying heads of departments: {str(e)}")

# Displaying Employees in a Certain Department
@cli.command()
@click.option('--department_name', prompt='Enter department name', type=str, callback=validate_name)
def display_employees_in_department(department_name):
    try:
        department = session.query(Department).filter_by(name=department_name).first()
        if department:
            employees = department.employees
            if employees:
                headers = ["Employee ID", "Employee Name"]
                data = [(employee.id, employee.name) for employee in employees]
                click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
            else:
                echo_success(f"No employees found in Department: {department_name}")
        else:
            echo_error(f"Department: {department_name} not found")
    except Exception as e:
        echo_error(f"Error displaying employees in department: {str(e)}")

# Displaying Projects Being Worked on by Departments
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
            click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
        else:
            echo_success("No departments found")
    except Exception as e:
        echo_error(f"Error displaying projects by departments: {str(e)}")


if __name__ == '__main__':
    cli()