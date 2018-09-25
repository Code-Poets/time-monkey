# time-monkey
Base application for management of employees working hours

Environment set-up

1.install python3.7
2.install pip
3.install virtualenv
4.virtualenv
5.install postgres
6.run postgres server
7.configure postgres
8.create db
9.clone repo
10.install requirements.lock
11.add local_settings.py

Linux



Mac OS



Windows
3.-4. same as mac (CMD /activate, PS ./activate)
5. desktop
8. PATH to lib and bin then command with password --> else pgadmin 4
9. same as mac
10 same as mac
11. DATABASES['default']['PASSWORD'] = ...

This project requires Python in version 3.7.0. If you're already using the same or higher version, you can skip the following step.

1. Get web-based Python installer from following link: 
        https://www.python.org/ftp/python/3.7.0/python-3.7.0-amd64-webinstall.exe
    You can also use alternative installer from Python's webpage at https://www.python.org/ftp/python/3.7.0/
    Once installer window pops up, make sure to toggle 'add to PATH' option before proceeding with installation.
    You can verify whether installation was successful by typing 'python'. A Python version should be displayed and Python interpreter should be running in the console. You can also verify successful pip installation by typing 'pip' in Command Line.

Skip this step if you have completed the previous step or have pip already installed.

2. Download the get-pip.py file from following link:
        https://bootstrap.pypa.io/get-pip.py
    Open Command Line and navigate to the location of the file. Then run 'python get-pip.py'.
    You can verify the installation by typing 'pip' in Command Line

3. If you don't have virtualenv installed, run installation with pip by typing 'pip install virtualenv' in Command Line

4. In Command Line, navigate to directory you wish to install virtual environment to and type 'virtualenv <name for your venv>'

5. To install PostgreSQL via Command Line, you will need to install BigSQL PGC. Navigate to directory where you want PostgreSQL to be installed and run the following command in Command Line: '@powershell -NoProfile -ExecutionPolicy unrestricted -Command "iex ((new-object net.webclient).DownloadString('https://s3.amazonaws.com/pgcentral/install.ps1'))"'
    After BigSQL PGC is installed, run the commands below to install and run PostgreSQL (ver. 10.5):
        cd bigsql
        pgc install pg10
        pgc start pg10              #evrytiem?

6. 

7.  Edit pg_hba.conf. If you installed PostgreSQL with BigSQL PGC, it should be located under \init\ folder in installation directory. Add the following line to file:
        local   all             postgres                                trust

8. In order to use PostgreSQL commands with Command Line, make sure to add folders 'lib' and 'bin' located in your PostgreSQL installation directory to your system's PATH. Then run the following command in Command Line: 'createdb -U postgres time_monkey'.
    If you installed pgadmin 4, you can use it to create new database as well. Make sure to name it 'time-monkey' and that it's assigned to user 'postgres'.

9. Navigate with Command Line to where you want the repository to be cloned and run 'git clone https://github.com/Code-Poets/time-monkey.git'

10. Use requirements.lock to install required pacakges to your virtual environment by running 'pip install -r requirements.lock'

11. Add 'local_settings.py' file to '/time_monkey/settings' directory and fill with following content:

        from .development import *

        ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', '192.168.8.9']
        
        SECRET_KEY = 'your secret key goes here'

    If you have set the password for your PostgreSQL server, make sure to include it in local settings, by writting the following line to the file:

        DATABASES['default']['PASSWORD'] = <your password>
