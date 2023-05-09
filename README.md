# django-importer
Another CSV importer based on Django.


## Default import log views
If you want to use the default import log views (list and detail), you should include in the template folder of your project `djimporter/base.html` template. This way you could set the layout and style of your project. For example the content could be:
```html
{% extends "myproject/base.html %}
{% block content %}{% endblock %}
```
## Custom import views
You need to create the import view form template in your project extending your base template. You can create basic importers or advanced importers using field mapper and separator guesser.

### Basic importer view

![simple_importer](https://github.com/ico-apps/django-importer/assets/2751315/fc310978-88ad-41ac-a45a-0992ec232845)
 
You can create a basic importer extending ImportFormView (from djimporter.views) and creating a template including a basic form:

```
<!-- include information on required fields and csv separator -->
{% include "djimporter/importer_info.html" %}

<form class="import-form" role="form" method="post" enctype="multipart/form-data">
{% csrf_token %}

<!-- Using bootstrap  libs -->
{% bootstrap_form form layout='horizontal' label_class='col-sm-2 col-form-label' field_class='col-sm-6'%}
<!-- Using django forms -->
{{ form }}

<button  class="btn btn-light border">{% trans 'Upload' %}</button>
</form>
```

### Advanced importer view

![advanced_importer](https://github.com/ico-apps/django-importer/assets/2751315/555ff9b4-9196-4af4-b3e1-8bf8b1704d34)


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
