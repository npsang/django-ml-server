# django-ml-aws-ec2

## Deploy machine learning Django App on AWS EC2

> ### Ubuntu 22 LTS set up

* `sudo apt-get update`

* `sudo apt-get upgrade`

* `sudo apt install python3-pip`

* `sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`

> ### Django ML AWS EC2 project set up

* `git clone https://github.com/npsang/django-ml-aws-ec2.git`

* `cd django-ml-aws-ec2`

* `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu`

* `pip3 install -r requirements.txt`

> ### Run project

* `cd MLRestAPI`

* `python3 manage.py runserver 0.0.0.0:8000`
    Then you can access project with url: <http://35.77.218.136:8000/>
