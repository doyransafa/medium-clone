# Medium Clone With Django

## Build Steps

Create a virtual environment

    python -m venv /path/to/new/virtual/environment

Activate virtual environment  
MacOS:

    source venv/bin/activate

for Windows PowerShell

    <venv_path>\Scripts\Activate.ps1  

Install dependencies 

    pip install -r requirements.txt

Migrate database  

    python manage.py makemigrations
    python manage.py migrate

Create admin user. Needed if you want to use Admin dashboard.

    python manage.py createsuperuser

Start server, port number is optional, default is 8000

    python manage.py runserver 8080
