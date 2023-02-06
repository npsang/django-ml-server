# django-ml-aws-ec2
Deploy machine learning Django App on AWS EC2

Ubuntu 22 LTS set up
    1. sudo apt-get update
    2. sudo apt-get upgrade
    3. sudo apt install python3-pip
    4. sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

Django ML AWS EC2 project set up
    1. git clone https://github.com/npsang/django-ml-aws-ec2.git
    2. cd django-ml-aws-ec2
    3. pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu 
    4. pip3 install -r requirements.txt

Run project
    1. cd MLRestAPI
    2. python3 manage.py runserver 0.0.0.0:8000
    Now you can access project with url: http://35.77.218.136:8000/

