# django-quick-context

A django app for quickly setting global context variables on all templates. 

It also allows fetching model instances from the database directly in the templates, which can be 
very useful in certain cases such as when the views are controlled by a third party app. 
See [Example 2](#example-2) for more.

## Installation

```
pip install django-quick-context
```

Then add `'quick_context.context_processors.quick'` to your `context_processors`:

```python
# settings.py

TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # ...
                'quick_context.context_processors.quick',
            ],
        },
    },
]
```

## Usage

### Example 1

Let's say you want to make a variable called `currency` available in all templates. 
Put this code in a file where it gets loaded on startup (such as project's or app's `__init__.py` or `apps.py` file).

```python
from quick_context import ContextRegistry

ContextRegistry.register(name='currency', value='USD')
```

The `quick_context` app makes a variable called `quick` available to every template. 
Every variable that you register with the `ContextRegistry`, it will be available 
as an attribute of the `quick` variable.

So, you can access the `currency` variable in the templates like this:

```
{{ quick.currency }}
```

### Example 2

This is a more useful case for using `quick_context`. 

Suppose you have a `Notice` model which allows you to display different notices 
on different pages in your website. For example, 'Home' page has a different notice 
and 'Contact' page has a different notice.

A sample `Notice` model: 

```python
# models.py

class Notice(models.Model):
    name = models.CharField(unique=True)
    message = models.CharField()

# Let's create a few notices
Notice.objects.create(name='homepage_notice', message='...')
Notice.objects.create(name='contact_notice', message='...')
Notice.objects.create(name='about_notice', message='...')
```

Now, to include a notice in the template, you'll have to send it the template 
context from the view:

```python
# views.py

def home_view(request):
    notice = Notice.objects.get(name='homepage_notice')
    context = {'notice': notice}

    return ...

def contact_view(request):
    # ... same as above ...

# repeat for other view ...
```

As you can see, this process is repetitve.

`quick_context` provides a better way to do it. 

First, register the `Notice` model:

```python
# models.py

from quick_context import ContextRegistry

class Notice(...):
    ...

ContextRegistry.register_model(name='notice', model=Notice, lookup_field='name')
```

Now, you can access a notice for a particular page without having to pass it 
from the views:

```
{{ quick.notice.homepage_notice.message }} -> displays message of "homepage_notice"

{{ quick.notice.contact_notice.message }} -> displays message of "contact_notice"
```

The `lookup_field` must be a field which has `unique=True`. This is important 
because behind the scenes, `quick_context` just does a `Model.objects.get(...)` lookup 
and `get` expects a single result from the database. If there are more than one results, 
Django will throw a `MultipleObjectsReturned` exception.

### Fetching multiple objects and filtering queryset

Since version 1.2, support for basic filtering has been added.

You can fetch multiple objects by applying a filter on the lookup field:

```
{% for notice in quick.notice.filter__icontains.homepage %}
     {{ notice.message }}
{% endfor %}
```

The above is equivalent to:

```python
Notice.objects.filter(name__icontains='homepage')
```

## API

#### `ContextRegistry.register(cls, name, value)`

Register a global context variable.

**`name`**: (string) Name of the variable.  
**`value`**: (any) A value for the variable. It can be anything: a string, a class, 
dictionary, etc. 

#### `ContextRegistry.register_model(cls, name, model, lookup_field)`

Register a model.

**`name`**: (string) Name of the variable.  
**`model`**: (class) The model class.  
**`lookup_field`**: (string) Name of the field to use for the lookup. Ensure that this 
field has `unique=True` because `quick_context` just does a `Model.objects.get(...)` 
lookup and `get` expects a single result from the database. If there are more than 
one results, Django will throw a `MultipleObjectsReturned` exception.

#### `ContextRegistry.update(cls, name, value)`

Updates the value of an already registered variable.

**`name`**: (string) Name of the variable.  
**`value`**: (any) New value for the variable.


#### `ContextRegistry.get_registry(cls)`

Returns a list of all the registered variables.

## License

[BSD-3-Clause](LICENSE.txt)