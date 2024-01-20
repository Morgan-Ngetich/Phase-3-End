import sys
import click
from tabulate import tabulate
from app.models import Department, Employee, Project
from app.models import Base
from app.database import session, engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

# Create tables in the database
Base.metadata.create_all(bind=engine)

def echo_error(message):
    click.secho(message, fg='red')

def echo_success(message):
    click.secho(message, fg='green')

def validate_name(ctx, param, value):
    if not value:
        raise click.BadParameter('Name cannot be empty.')
    if not value.isalpha():
        raise click.BadParameter('Name should only contain alphabets.')
    return value

def validate_positive_int(ctx, param, value):
    if not value:
        raise click.BadParameter('ID cannot be empty.')
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValueError
        return int_value
    except ValueError:
        raise click.BadParameter('ID should be a positive integer.')
    

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
            entity_id = click.prompt(f'Enter the ID of the {entity.__name__.lower()} to remove', type=click.IntRange(1))
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

def add_employees_to_department():
    try:
        # Display the departments table for the user to select
        departments = session.query(Department).all()
        if not departments:
            click.echo("No departments found. Please add a department first.")
            return

        headers = ["ID", "Name"]
        data = [(department.id, department.name) for department in departments]
        click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))

        # Prompt user to select a department
        department_id = click.prompt('Choose a department ID to add employees to', type=int)
        department = session.query(Department).filter_by(id=department_id).first()

        if not department:
            click.secho(f"Department with ID {department_id} not found.", fg='red')
            return

        # Filter employees not assigned to any departments
        available_employees = (
            session.query(Employee)
            .filter(Employee.department_id.is_(None))
            .options(joinedload(Employee.projects))
            .all()
        )

        if not available_employees:
            click.secho("No available employees to add to the department.", fg='red')
            return

        # Display the table of employees not assigned to any departments
        headers = ["ID", "Name", "Projects"]
        data = [(employee.id, employee.name, ', '.join([project.name for project in employee.projects])) for employee in available_employees]
        click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))

        # Prompt user to select employee IDs to add (comma-separated)
        employee_ids_str = click.prompt('Enter the IDs of the employees to add (comma-separated)', type=str)
        employee_ids = [int(e_id) for e_id in employee_ids_str.split(',') if e_id.isdigit()]

        # Add selected employees to the department
        for employee_id in employee_ids:
            employee = session.query(Employee).filter_by(id=employee_id).first()
            if employee:
                employee.department_id = department.id
            else:
                click.secho(f"Employee with ID {employee_id} not found.", fg='red')

        session.commit()

        click.secho(f"Employees added to department {department.name}", fg='green')

    except Exception as e:
        click.secho(f"Error adding employees to department: {str(e)}", fg='red')
   

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
                click.echo(f"No employees found in Department: {department_name}")
        else:
            click.echo(f"Department: {department_name} not found")
    except Exception as e:
        click.echo(f"Error displaying employees in department: {str(e)}")
        

def assign_projects_to_employees_in_department():
    try:
        # Display the departments table for the user to select
        departments = session.query(Department).all()
        if not departments:
            click.echo("No departments found. Please add a department first.")
            return

        headers = ["ID", "Name"]
        data = [(department.id, department.name) for department in departments]
        click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))

        # Prompt user to select a department
        department_id = click.prompt('Choose a department ID to assign projects to employees', type=int)
        department = session.query(Department).filter_by(id=department_id).first()

        if not department:
            click.secho(f"Department with ID {department_id} not found.", fg='red')
            return

        # Display the projects table for the user to select
        projects = session.query(Project).filter_by(department_id=department.id).all()

        if not projects:
            click.echo(f"No projects found in Department: {department.name}. Please add a project first.")
            return

        headers = ["ID", "Name"]
        data = [(project.id, project.name) for project in projects]
        click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))

        # Prompt user to select project IDs to assign (comma-separated)
        project_ids_str = click.prompt('Enter the IDs of the projects to assign (comma-separated)', type=str)
        project_ids = [int(p_id) for p_id in project_ids_str.split(',') if p_id.isdigit()]

        # Assign selected projects to employees in the department
        for project_id in project_ids:
            project = session.query(Project).filter_by(id=project_id, department_id=department.id).first()
            if project:
                project.employees = department.employees
            else:
                click.secho(f"Project with ID {project_id} not found in Department: {department.name}.", fg='red')

        session.commit()

        click.secho(f"Projects assigned to employees in department {department.name}", fg='green')

    except Exception as e:
        click.secho(f"Error assigning projects to employees in department: {str(e)}", fg='red')
        
# Function to view the employee info
def view_employee_info():
    try:
        # Prompt user to enter their employee ID
        employee_id = click.prompt('Enter your employee ID', type=int)
        employee = session.query(Employee).filter_by(id=employee_id).first()

        if not employee:
            echo_error(f"Employee with ID {employee_id} not found.")
            return

        # Display information about the employee's department
        department = employee.department
        if department:
            echo_success(f"You are part of the '{department.name}' department.")

            # Display projects assigned to the employee
            projects = employee.projects
            if projects:
                headers = ["Project ID", "Project Name"]
                data = [(project.id, project.name) for project in projects]
                click.echo(tabulate(data, headers=headers, tablefmt="grid", numalign="center"))
            else:
                echo_success("You are not assigned to any projects.")
        else:
            echo_success("You are not assigned to any department.")

    except Exception as e:
        echo_error(f"Error viewing employee information: {str(e)}")
    
                
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

# Add employees to a department
@cli.command()
def add_employees_to_a_department():
    add_employees_to_department()
    
# Assign projects to employees in a department
@cli.command()
def assign_projects_to_employees():
    assign_projects_to_employees_in_department()
    
# View the employee info
@click.command()
def view_my_info():
    view_employee_info()    
cli.add_command(view_my_info)  
        
if __name__ == '__main__':
    cli()