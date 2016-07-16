#!//usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License - full license can be found in LICENSE file.
# Copyright (c) 2016 Jan Nakladal

from __future__ import unicode_literals, absolute_import

import time
from collections import namedtuple

import pytest
from django.core.cache import caches
from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT, \
    InvalidCacheBackendError

from django_in_request_cache.cache import CacheACache


###############################################################################
#  Test Fixtures
###############################################################################


CacheItem = namedtuple('CacheItem', ['value', 'expire_at', 'timeout'])


class MockCache(BaseCache):

    def __init__(self, location, params):
        self.name = location
        self.cache = {}
        super(MockCache, self).__init__(params)

    def cache_key(self, key, version=None):
        """
        Constructs and validate the key used by all other methods.
        """
        self.validate_key(key)
        return key

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        """
        key = self.cache_key(key, version=version)
        expiration_time = self.get_backend_timeout(timeout)
        self.cache[key] = CacheItem(value, expiration_time, timeout)

    def get(self, key, default=None, version=None):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        key = self.cache_key(key, version=version)
        item = self.cache.get(key)
        if isinstance(item, CacheItem) and time.time() < item.expire_at:
            return item.value

        return default

    def delete(self, key, version=None):
        """
        Delete a key from the cache, failing silently.
        """
        key = self.cache_key(key, version=version)
        try:
            del self.cache[key]
        except KeyError:
            pass  # delete method fails silently.

    def clear(self):
        """
        Remove *all* values from the cache at once.
        """
        self.cache = {}

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Set a value in the cache if the key does not already exist. If
        timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.

        Returns True if the value was stored, False otherwise.
        """
        if not self.has_key(key, version):
            self.set(key, value, timeout, version)
            return True

        return False

    def has_key(self, key, version=None):
        """
        Returns True if the key is in the cache and has not expired.
        """
        cache_key = self.cache_key(key, version=version)
        if cache_key not in self.cache:
            return False

        return super(MockCache, self).has_key(key, version)


@pytest.fixture()
def main_cache():
    cache = caches['main_cache']
    cache.clear()
    return cache


@pytest.fixture()
def fast_cache():
    cache = caches['fast_cache']
    cache.clear()
    return cache


def get_cache(**kwargs):
    location = kwargs.pop('location', None)
    params = dict(
        fast_cache='fast_cache',
        cache_to_cache='main_cache',
    )
    params.update(kwargs)
    return CacheACache(location, params)


def assert_item(cache, key, value, timeout):
    assert key in cache.cache
    item = cache.cache[key]
    assert item.value == value
    assert item.timeout == timeout


###############################################################################
#  Test CacheACache
###############################################################################


def test_cache_property(main_cache, fast_cache):
    cache = get_cache()
    assert cache.cache is main_cache
    assert cache.fast_cache is fast_cache


def test_wrong_cache_property():
    cache = get_cache(fast_cache='wrong_cache', cache_to_cache='bad_cache')
    with pytest.raises(InvalidCacheBackendError) as exc_info:
        cache_to_cache = cache.cache
    assert 'bad_cache' in exc_info.value.message

    with pytest.raises(InvalidCacheBackendError) as exc_info:
        fast_cache = cache.fast_cache
    assert 'wrong_cache' in exc_info.value.message


def test_fast_cache_set(fast_cache):
    cache = get_cache(fast_cache_max_timeout=5)
    assert 'key' not in fast_cache.cache
    cache.fast_cache_set('key', 'value')
    assert_item(fast_cache, 'key', 'value', timeout=5)

    assert 'key2' not in fast_cache.cache
    cache.fast_cache_set('key2', 'value2', timeout=10)
    assert_item(fast_cache, 'key2', 'value2', timeout=5)

    assert 'key3' not in fast_cache.cache
    cache.fast_cache_set('key3', 'value3', timeout=3)
    assert_item(fast_cache, 'key3', 'value3', timeout=3)


def test_cache_set(fast_cache, main_cache):
    cache = get_cache(fast_cache_max_timeout=5, timeout=10)

    assert 'key' not in fast_cache.cache
    assert 'key' not in main_cache.cache
    cache.set('key', 'value')
    assert_item(fast_cache, 'key', 'value', timeout=5)
    assert_item(main_cache, 'key', 'value', timeout=10)

    assert 'key2' not in fast_cache.cache
    assert 'key2' not in main_cache.cache
    cache.set('key2', 'value2', timeout=15)
    assert_item(fast_cache, 'key2', 'value2', timeout=5)
    assert_item(main_cache, 'key2', 'value2', timeout=15)

    cache.set('key', 'value3', timeout=3)
    assert_item(fast_cache, 'key', 'value3', timeout=3)
    assert_item(main_cache, 'key', 'value3', timeout=3)


def test_cache_get(fast_cache, main_cache):
    cache = get_cache(fast_cache_max_timeout=5, timeout=10)

    assert 'key' not in fast_cache.cache
    assert 'key' not in main_cache.cache
    assert 'default' == cache.get('key', 'default')

    main_cache.set('key', 'value', timeout=222)
    assert_item(main_cache, 'key', 'value', timeout=222)
    assert 'key' not in fast_cache.cache
    assert 'value' == cache.get('key', 'value')
    assert_item(fast_cache, 'key', 'value', timeout=5)

    main_cache.delete('key')
    assert 'key' not in main_cache.cache
    assert 'value' == cache.get('key', 'value')
    assert_item(fast_cache, 'key', 'value', timeout=5)


def test_cache_delete(fast_cache, main_cache):
    cache = get_cache()

    fast_cache.set('key', 'value')
    assert 'key' in fast_cache.cache
    assert 'key' not in main_cache.cache
    cache.delete('key')
    assert 'key' not in fast_cache.cache
    assert 'key' not in main_cache.cache

    main_cache.set('key', 'value')
    assert 'key' not in fast_cache.cache
    assert 'key' in main_cache.cache
    cache.delete('key')
    assert 'key' not in fast_cache.cache
    assert 'key' not in main_cache.cache


def test_cache_clear(fast_cache, main_cache):
    cache = get_cache()
    fast_cache.set('key', 'value')
    main_cache.set('key', 'value')
    assert len(fast_cache.cache)
    assert len(main_cache.cache)
    cache.clear()
    assert not len(fast_cache.cache)
    assert not len(main_cache.cache)


def test_cache_add(fast_cache, main_cache):
    cache = get_cache(fast_cache_max_timeout=5, timeout=10)

    fast_cache.set('key', 'default', timeout=3)
    assert_item(fast_cache, 'key', 'default', timeout=3)
    assert 'key' not in main_cache
    assert cache.add('key', 'value')
    assert_item(fast_cache, 'key', 'value', timeout=5)
    assert_item(main_cache, 'key', 'value', timeout=10)
