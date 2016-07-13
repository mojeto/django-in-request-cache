#!//usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License - full license can be found in LICENSE file.
# Copyright (c) 2016 Jan Nakladal

from __future__ import unicode_literals, absolute_import

import time
import warnings

import django_globals
import pytest
from django.test import Client
from django_globals.middleware import Global, globals as d_globals

from django_in_request_cache.cache import InRequestCache, CacheItem


class MockRequest(object):
    """
    Mock django request object for testing purpose
    """


@pytest.fixture()
def global_request():
    request = MockRequest()
    Global().process_request(request)
    return request


def test_global_request_fixture(global_request):
    assert global_request is django_globals.globals.request


def test_cache_in_request(client):
    assert isinstance(client, Client)


def test_cache_set(global_request):
    cache = InRequestCache(location=None, params={})
    cache.set('key', 'value')
    item = getattr(global_request, cache.cache_name)[cache.cache_key('key')]
    assert isinstance(item, CacheItem)
    assert item.value == 'value'


def test_cache_set_timeout(global_request):
    cache = InRequestCache(location=None, params={})
    timeout = 2
    start = time.time()
    cache.set('key', 'value', timeout=timeout)
    end = time.time()
    item = getattr(global_request, cache.cache_name)[cache.cache_key('key')]
    assert isinstance(item, CacheItem)
    assert item.expire_at >= start + timeout
    assert item.expire_at <= end + timeout


def test_cache_get(global_request):
    cache = InRequestCache(location=None, params={})
    expire_at = time.time()
    cache_data = {
        cache.cache_key('key'): CacheItem('value', expire_at),
        cache.cache_key('key2'): CacheItem('value2', expire_at + 2),
    }
    setattr(global_request, cache.cache_name, cache_data)

    assert cache.get('key', default='default') == 'default'
    assert cache.get('key2') == 'value2'


def test_cache_add(global_request):
    cache = InRequestCache(location=None, params={})
    cache_data = {
        cache.cache_key('key'): CacheItem('value', time.time() + 10)
    }
    setattr(global_request, cache.cache_name, cache_data)

    assert cache.add('key', 'value2') == False
    assert cache.get('key') == 'value'

    assert cache.add('key2', 'value2') == True
    assert cache.get('key2') == 'value2'


def test_missing_request_warning(global_request):
    cache = InRequestCache(location=None, params={})
    delattr(d_globals, 'request')
    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")
        # Trigger a warning.
        assert cache.get('key', default='default') == 'default'
        # Verify warning
        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert "Missing django request object" in str(w[-1].message)


def test_cache_clear(global_request):
    cache = InRequestCache(location=None, params={})
    in_request_cache = cache.cache
    assert in_request_cache is getattr(global_request, cache.cache_name)
    cache.clear()
    assert in_request_cache is not getattr(global_request, cache.cache_name)
    assert in_request_cache is not cache.cache
    assert cache.cache is getattr(global_request, cache.cache_name)


def test_cache_delete(global_request):
    cache = InRequestCache(location=None, params={})
    cache_key = cache.cache_key('key')
    cache_data = {
        cache_key: CacheItem('value', time.time() + 10)
    }
    setattr(global_request, cache.cache_name, cache_data)
    assert cache_key in cache_data
    cache.delete('key')
    assert cache_key not in cache_data


def test_cache_get_backend_timeout(global_request):
    max_timeout = 2
    default_timeout = 10
    cache = InRequestCache(location=None, params={
        'MAX_TIMEOUT': max_timeout, 'TIMEOUT': default_timeout,
    })
    start = time.time()
    timeout = cache.get_backend_timeout()
    end = time.time()
    assert timeout >= start + max_timeout
    assert timeout <= end + max_timeout

    start = time.time()
    timeout = cache.get_backend_timeout(timeout=1)
    end = time.time()
    assert timeout >= start + 1
    assert timeout <= end + 1


def test_cache_without_global_request(global_request):
    delattr(d_globals, 'request')
    cache = InRequestCache(location=None, params={})
    assert cache.get('key') is None
    cache.set('key', 'value')
    assert cache.get('key') is None
