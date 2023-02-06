# django-ml-aws-ec2
<h1>Deploy machine learning Django App on AWS EC2</h1>

<h2>Ubuntu 22 LTS set up</h2>
<ol>
    <li>sudo apt-get update</li>
    <li>sudo apt-get upgrade</li>
    <li>sudo apt install python3-pip</li>
    <li>sudo apt-get install python3-dev default-libmysqlclient-dev build-essential</li>
</ol>
<h2>Django ML AWS EC2 project set up</h2>
<ol>
    <li>git clone https://github.com/npsang/django-ml-aws-ec2.git</li>
    <li>cd django-ml-aws-ec2</li>
    <li>pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu</li>
    <li>pip3 install -r requirements.txt</li>
</ol>
<h2>Run project</h2>
<ol>
    <li>cd MLRestAPI</li>
    <li>python3 manage.py runserver 0.0.0.0:8000<li>
    Now you can access project with url: http://35.77.218.136:8000/
</ol>
