import click
from app.models import Department
from app.models import Employee
from app.models import Project
from app.database import session

@click.group()
def cli():
    pass

# Adding a Department
@cli.command()
@click.option('--name', prompt='Enter department name')
def add_department(name):
    try:
        if not name:
            raise ValueError("Department name cannot be empty")
        
        new_department = Department(dept_name=name)
        session.add(new_department)
        session.commit()
        click.echo(f"Added department: {name}")
        display_departments()
    except Exception as e:
        click.echo(f"Error adding department: {str(e)}")

# Deleting a Department
@cli.command()
@click.option('--id', prompt='Enter department ID', type=int)
def delete_department(id):
    try:
        department = session.query(Department).filter_by(id=id).first()
        if department:
            session.delete(department)
            session.commit()
            click.echo(f"Deleted department with ID: {id}")
            display_departments()
        else:
            click.echo(f"Department with ID {id} not found")
    except Exception as e:
        click.echo(f"Error deleting department: {str(e)}")

# Displaying All Departments
@cli.command()
def display_departments():
    try:
        departments = session.query(Department).all()
        if departments:
            click.echo("List of Departments:")
            for department in departments:
                click.echo(f"ID: {department.id}, Name: {department.dept_name}")
        else:
            click.echo("No departments found")
    except Exception as e:
        click.echo(f"Error displaying departments: {str(e)}")



if __name__ == '__main__':
    cli()
