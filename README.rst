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
            # 'LOCATION': '_dinr_cache',  # request property name to store data
            # 'OPTIONS': {
            #     # if set then no value is stored for more than MAX_TIME time.
            #     'MAX_TIMEOUT': 10,  # in seconds,
            # },
        },
    )

2. Add django-globals middleware to your settings like this::

    MIDDLEWARE_CLASSES = [
        ...,
        'django_globals.middleware.Global',
    ]


Configuration
-------------

* How to cache a slower but cross process cache backend::

    from django.conf.global_settings import CACHES as DEFAULT_CACHES

    CACHES = dict(
        DEFAULT_CACHES,
        redis_cache = {
            'BACKEND: 'redis_cache.RedisCache',
            ...
        },
        cache_in_request={
            'BACKEND': 'django_in_request_cache.cache.InRequestCache',
            'LOCATION': '_redis_cache_mirror',  # request property name
        },
        combined_in_request_and_redis_cache={
            'BACKEND': 'django_in_request_cache.cache.CacheACache',
            'OPTIONS: {
                'FAST_CACHE': 'cache_in_request',  # cache alias
                'FAST_CACHE_MAX_TIMEOUT': 5,  # in seconds
                'CACHE_TO_CACHE': 'redis_cache',  # cache alias
            },
        },
    )

Requirements
------------

* `Django`_ >= 1.6
* `django-globals`_ >= 0.2


License
-------

* `The MIT License`_

.. _The MIT License: https://raw.githubusercontent.com/mojeto/django-in-request-cache/master/LICENSE
.. _Django: https://github.com/django/django
.. _django-globals: https://github.com/svetlyak40wt/django-globals