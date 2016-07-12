django-in-request-cache
=======================

Django cache backend stored in django request 

.. image:: https://travis-ci.org/mojeto/django-in-request-cache.svg?branch=master
    :target: https://travis-ci.org/mojeto/django-in-request-cache

Installation
------------

.. code-block:: bash

    $ pip install django-in-request-cache
    
Quick start
-----------

1. Add "django-in-request-cache" to your setting as cache like this::

    from django.conf.global_settings import CACHES as DEFAULT_CACHES
    
    CACHES = dict(
        DEFAULT_CACHES,
        cache_in_request={
            'BACKEND': 'django_in_request_cache.cache.InRequestCache',
            # 'LOCATION': 'my_request_cache',  # request property name to store data
            # 'OPTIONS': {},
        },
    )

2. Add django-globals middleware to your settings like this::

    MIDDLEWARE_CLASSES = [
        ...,
        'django_globals.middleware.Global',
    ]

License
-------

* `The MIT License`_

.. _The MIT License: https://raw.githubusercontent.com/mojeto/django-in-request-cache/master/LICENSE
