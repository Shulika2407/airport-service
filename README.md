# airport-service
Implementation of a system for tracking flights from airports around the world

![img.png](img.png)


Run with docker
---------------
- docker-compose build 
- docker-compose up

Getting access
--------------
- create user via /api/customer/register/
- get access token via /api/customer/token/

# Installing using GitHub

Install PostgresSQL and create db
---------------------------------

git clone https://github.com/Shulika2407/airport-service.git

cd airport-service

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

set DB_HOST=<"your db hostname">

set DB_NAME=<"your db name">

set DB_USER=<"your db username">

set DB_PASSWORD=<"your db user password">

set SECRET_KEY=<"your secret key">

python manage.py migrate

python manage.py runserver