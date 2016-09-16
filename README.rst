django-in-request-cache
=======================

Django cache backend stored in django request 

.. image:: https://travis-ci.org/mojeto/django-in-request-cache.svg?branch=master&maxAge=259200
    :target: https://travis-ci.org/mojeto/django-in-request-cache

.. image:: https://img.shields.io/pypi/v/django-in-request-cache.svg?maxAge=259200
    :target: https://pypi.python.org/pypi/django-in-request-cache

.. image:: https://img.shields.io/pypi/l/django-in-request-cache.svg?maxAge=2592000
    :target: https://raw.githubusercontent.com/mojeto/django-in-request-cache/master/LICENSE

Installation
------------

.. code-block:: bash

    $ pip install django-in-request-cache
    
Fast InRequestCache
-------------------

InRequestCache is implementation of django cache interface.
It uses instance of python dict assigned to each django request object to store cached values.
`django-globals`_ is used to make request object accessible everywhere.
This cache has the same limitations as standard django InMemory cache - Cross process access isn't possible.
InRequestCache goes one step further and makes cross thread access impossible.
InRequestCache is different in each request.
InRequestCache should be faster than InMemory cache, because there is no read/write lock.
It makes sense to use InRequestCache for values which will be accessible multiple times in the same request.
Cache invalidation is hard, but because cache lives for request period only it isn't a big problem.

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


Speed up slower cache with faster cache
---------------------------------------

Why do we want to cache a cache?
In my case I have one value in redis cache, which was accessed 20 times during the same django request.
Every read from redis takes ~1ms, it makes ~20ms just read the same value 20 times.
To speed it up I want cache my value in faster cache (InRequestCache, InMemoryCache etc.)
CacheACache class is implementation of django cache interface which allows read value from slower cache
only once and 'cache' it again in faster in memory cache.
Most of the time faster cache is back populated from slower cache. In this case we doesn't have information whe value expire.
In that case cache max expiration time for cached value is value expire time + slow cache expiration time.
Therefore fast cache expiration time **should be set very low** (in number of seconds).

CacheACache configuration
-------------------------

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