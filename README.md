# Got It's SWE Final Project

## Requirements

- Python 3.7+
- MySQL 5.7+

## Installation

### Set up virtual environment

```shell
pip install virtualenv
virtualenv venv
source ./venv/bin/activate
```

### Install dependencies

```shell
pip install -r requirements-dev.txt
```

### Install `pre-commit` hooks

- Install `pre-commit`: https://pre-commit.com/
- Install `pre-commit` hooks:

  ```shell
  pre-commit install
  ```

## Migrate database
- Create a `catalog` and `catalog_test` schema in MySQL
- Update URI and password in `/config/base.py` and `/config/test.py`. 
  - URI should have the form: `"mysql+pymysql://root:{password}@{database_uri}/catalog"`
- Migrate
  ```
  flask db upgrade
  ```

## Running

### Set environment
```
export FLASK_ENV={local/development/production/test}
```

### Start server
Inside the virtual environment, run

```shell
python run.py
```

