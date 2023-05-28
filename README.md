# Pass Finder
[Логика проекта и структура данных](https://www.figma.com/file/2De9jBDhNbFg8ScjKGmorY/Untitled?type=whiteboard&node-id=0%3A1&t=NGIe9sKMeVjNiK9j-1)

## Basic Commands

### Load data
be sure to create .env file in top directory(clone .env.template)

    $ ./manage.py migrate
    $ ./manage.py loaddata data.json

data.json can be downloaded here: https://akarpov.ru/media/passfinder/data.json

### Runserver

    $ ./manage.py runserver_plus

### Type checks

Running type checks with mypy:

    $ mypy passfinder

#### Running tests with pytest

    $ pytest

### Setting Up Your Users

-   To create a **superuser account**, use this command:

        $ python manage.py createsuperuser

### Celery

This app comes with Celery.

To run a celery worker:

``` bash
celery -A config.celery_app worker -B -l warning
```


made with [cookiecutter-django](https://github.com/Alexander-D-Karpov/cookiecutter-django)
