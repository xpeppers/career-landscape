# Career Landscape

...

## Dependencies

You need this installs to proceed:

- [Virtualbox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)

## Enviroment Variables

Create a .env file with these variables:

DJ_SECRET_KEY
DJ_DEBUG
DJ_DB_NAME
DJ_DB_USER
DJ_DB_PSW
DJ_HOST
DJ_PORT

## Instructions

Development setup, run these commands:

```
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

```
python3 manage.py test
```


## Run

To run the application:

```
python3 manage.py runserver 0:8000
```

Go to http://127.0.0.1:8080/ to see your app.
