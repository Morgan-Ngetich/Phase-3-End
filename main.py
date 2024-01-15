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

def validate_name(ctx, param, value):
    if not value:
        raise click.BadParameter('Name cannot be empty.')
    return value

def add_entity(entity, name, **kwargs):
    try:
        new_entity = entity(name=name, **kwargs)
        session.add(new_entity)
        session.commit()
        echo_success(f"Added {entity.__name__.lower()}: {name}")
        display_entities(entity)
    except Exception as e:
        echo_error(f"Error adding {entity.__name__.lower()}: {str(e)}")

def remove_entity(entity, name):
    try:
        entity_instance = session.query(entity).filter_by(name=name).first()
        if entity_instance:
            session.delete(entity_instance)
            session.commit()
            echo_success(f"Removed {entity.__name__.lower()}: {name}")
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


# Adding a Department
@cli.command()
@click.option('--name', prompt='Enter department name', callback=validate_name)
def add_department(name):
    try:
        employees = session.query(Employee).all()
        if employees:
            headers = ["ID", "Name"]
            data = [(employee.id, employee.name) for employee in employees]
            click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
            head_of_dept_id = click.prompt('Choose an employee ID to be the head of the department', type=int)

            head_of_dept = session.query(Employee).filter_by(id=head_of_dept_id).first()
            if head_of_dept:
                add_entity(Department, name, head_of_department=head_of_dept)
            else:
                echo_error(f"Employee with ID {head_of_dept_id} not found.")
        else:
            echo_error("No employees found. Please add an employee first.")
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
        if departments:
            headers = ["ID", "Name"]
            data = [(department.id, department.name) for department in departments]
            click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
            department_name = click.prompt('Choose a department name to assign the employee to', type=str)

            department = session.query(Department).filter_by(name=department_name).first()
            if department:
                add_entity(Employee, name, department_id=department.id)
            else:
                echo_error(f"Department '{department_name}' not found.")
        else:
            # No departments available, create an employee without associating it with any department
            add_entity(Employee, name)
    except Exception as e:
        echo_error(f"Error adding employee: {str(e)}")

# Removing an Employee
@cli.command()
@click.option('--name', prompt='Enter employee name', callback=validate_name)
def remove_employee(name):
    remove_entity(Employee, name)

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
    remove_entity(Project, name)

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
