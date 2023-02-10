# django ml server for compute document similarity web app

## Deploy machine learning Django App on AWS EC2

> ### Window set up for localhost

1. Install python 3.10.6
   * Windows installer (32-bit) <https://www.python.org/ftp/python/3.10.6/python-3.10.6.exe>
   * Windows installer (64-bit) <https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe>
   * Should select install for all users, and Add to PATH
   * Check if python installed with command `python --version`
2. Create python virtual environment
   * Open Terminal or Powershell
   * `mkdir DATN`
   * `cd DATN`
   * `git clone https://github.com/npsang/django-ml-server.git`
   * `cd django-ml-server`
   * `python -m pip install --upgrade pip setuptools wheel`
   * `python -m venv ml_env`
   * `ml_env\Scripts\activate` The terminal should show something like '(ml_env) ~\DATN\django-ml-server\"'
   * `python -m pip install --upgrade pip setuptools wheel`
   * `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117`
   * `pip install -r requirements.txt`
3. Run
   * `cd MLRestAPI`
   * `python manage.py makemigrations`
   * `python manage.py migrate`
   * `python manage.py runserver`
4. Next time run
   * `ml_env\Scripts\activate`
   * `cd MLRestAPI`
   * `python manage.py makemigrations`
   * `python manage.py migrate`
   * `python manage.py runserver`

> ### Window Set up with IIS

1. Create python virutal environment and active
   > `cd C:\`
   > `mkdir pyenv`
   > `cd pyenv`
   > `python -m venv djangoML`
   > `.\djangoML\Scripts\activate`
   Now environment is djangoML
   > `python -m pip install --upgrade pip`
2. Clone project
   > `git clone https://github.com/npsang/django-ml-aws-ec2.git`
   > `cd django-ml-aws-ec2`
3. `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117`
4. `pip install -r .\requirements.txt`
5. Install MySQL
6. Connect MySQL

> ### Ubuntu 22 LTS set up

1. `sudo apt-get update`

2. `sudo apt-get upgrade`

3. `sudo apt install python3-pip`

4. `sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`

5. `pip install -r .\requirements.txt`

> ### Django ML AWS EC2 project set up

1. `git clone https://github.com/npsang/django-ml-aws-ec2.git`

2. `cd django-ml-aws-ec2`

3. `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu`

4. `pip3 install -r requirements.txt`

> ### Run project

1. `cd MLRestAPI`

2. `python3 manage.py runserver 0.0.0.0:8000`
    Then you can access project with url: <http://35.77.218.136:8000/>

>            #         """  
            #         # 1. set the field to Django BinaryField
            #         from django.db import models
            #         np_field = models.BinaryField()
            #         # 2. transform numpy array to python byte using pickle dumps, then encoded by base64
            #         # np_bytes = pickle.dumps(np_array)
            #         np_base64 = base64.b64encode(np_bytes)
            #         model.np_field = np_base64
            #         # 3. get the numpy array from django model
            #         np_bytes = base64.b64decode(model.np_field)
            #         np_array = pickle.loads(np_bytes)
            #         """`
