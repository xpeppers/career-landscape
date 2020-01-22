# Career Landscape

[![Build Status](https://travis-ci.com/xpeppers/career-landscape.svg?branch=master)](https://travis-ci.com/xpeppers/career-landscape)

## Dependencies

You need this installs to proceed:

- [Virtualbox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)

## Enviroment Variables

Create a .env file with these variables:

- DJ_SECRET_KEY="random secret key"
- DJ_DEBUG="1" for True or "0"
- DJ_DB_NAME="a database name"
- DJ_DB_USER="a database user"
- DJ_DB_PSW="the user password"
- DJ_DB_HOST="localhost"
- DJ_DB_PORT="" for local development

## Instructions

Development setup, run these commands:

```blank
vagrant up
vagrant ssh
cd /vagrant/
pipenv install
pipenv shell
python3 manage.py migrate
python3 manage.py createsuperuser
```

## Run Tests

For testing the application:

```blank
python3 manage.py test
```

### Get tests coverage

Run:

```blank
coverage run --source='.' manage.py test
```

To see the report run:

```blank
coverage report
```

## Run Linter

For testing the application:

```blank
black ./
```

## Populate DB

Apply seed sample dataset

```blank
python3 manage.py loaddata seed.json
```

## Run

To run the application:

```blank
python3 manage.py runserver 0:8000
```

Go to http://127.0.0.1:8080/ to see your app.
