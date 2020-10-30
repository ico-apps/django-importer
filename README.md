# django-importer
Another CSV importer based on Django.


## Default import log views
If you want to use the default import log views (list and detail), you should include in the template folder of your project `djimporter/base.html` template. This way you could set the layout and style of your project. For example the content could be:
```html
{% extends "myproject/base.html %}
{% block content %}{% endblock %}
```

## Installation
Install the package using pip:
```bash
pip install djimporter
```

Update `INSTALLED_APPS` of `settings.py` of the project:
```python
INSTALLED_APPS = [
    ...
    'background_task',
    'djimporter',
]
```

## Configuration
django-importer supports using a custom model for ImportLogs. It can be configured via project settings.py:
```
IMPORT_LOG_MODEL = 'yourapp.CustomImportLog'
```

The recommeded way is to create a `CustomImportLog` model that extends abstract model `AbstractBaseLog`.


## Run tests
Only 3 steps are required to run the test suite based on [pytest](https://docs.pytest.org/):
```
# 1. clone the repository
git clone https://github.com/ico-apps/django-importer.git

# 2. prepare virtualenv and install dependencies
cd django-importer
python3 -m virtualenv -p /usr/bin/python3 env
source env/bin/activate
pip install -r requirements.txt
pip install -r tests/requirements.txt
cp djimporter/templates/djimporter/base.example.html djimporter/templates/djimporter/base.html

# 3. run test suite!
pytest
```
