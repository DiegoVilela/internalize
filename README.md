# Internalize

This project is an exercise to apply the concepts of the Django web
framework and Python.

The purpose of the app is to ease the transit of configuration
item data between an IT managed services provider (MSP) and
its clients.


## Authors

- [@diegovilela](https://www.github.com/diegovilela)


## Demo

You can access it with the following credentials.

| username | password | login page |
| -------- | -------- | -----------|
| admin | UnQt5uGgjErbwkN | [for admins][2]
| client_a_user@example.com | UnQt5uGgjErbwkN | [for users][1]
| client_b_user@example.com | UnQt5uGgjErbwkN | [for users][1]

[1]: https://secure-forest-64714.herokuapp.com/cis/cis/0/
[2]: https://secure-forest-64714.herokuapp.com/admin/


## Features

- Admin area
- Bulk insertion of items
- Bulk approval of items
- Responsive


## Running Tests

To run only unit tests:
```bash
  python manage.py test --exclude-tag functional
```

To also run functional tests (requires [geckodriver](https://github.com/mozilla/geckodriver/releases)):
```bash
  python manage.py test
```


## Installation

```bash
  git clone https://github.com/DiegoVilela/internalize.git
  cd internalize
  pipenv install && pipenv shell
  python manage.py migrate
  python manage.py loaddata all.json
  python manage.py runserver
```

## Feedback

If you have any feedback, please reach out to us at vilelaphp@gmail.com
