# automactic
A custom-built internal solution for adding MAC Addresses to Aruba Clearpass. An architecture overview can be found here.

[comment]: <> (TODO: Link the architecture overview)

### Development Environment
Prerequisites:
- Poetry
- Postgres

Setup:
* Install latest supported version of Python as specified in `pyproject.toml`
  * This can be done using pyenv or using your system packages.
* Instantiate the virtualenv and a shell:
  ```bash
  $ poetry install
  $ poetry shell
  ```
* If a database does not exist yet, make migrations and install the fixtures:
  ```bash
  $ python manage.py makemigrations
  $ python manage.py migrate
  $ python manage.py loaddata admin_permissions
  ```
* Start the development server on `localhost:8000` by running:
  ```bash
  $ python manage.py runserver
  ```
