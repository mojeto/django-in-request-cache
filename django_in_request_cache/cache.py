#!//usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License - full license can be found in LICENSE file.
# Copyright (c) 2016 Jan Nakladal

from __future__ import unicode_literals, absolute_import

import collections
import time
import warnings

from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT
from django_globals import globals as d_global


CacheItem = collections.namedtuple('CacheItem', ['value', 'expire_at'])


class InRequestCache(BaseCache):
    cache_name = '_dinr_cache'
    max_timeout = None

    def __init__(self, params):
        super(InRequestCache, self).__init__(params)
        self.cache_name = params.get('cache_name', params.get('CACHE_NAME')) \
            or self.cache_name
        self.max_timeout = int(
            params.get('max_timeout', params.get('MAX_TIMEOUT')) or
            self.default_timeout
        )

    @property
    def request(self):
        """
        get current django request object
        :return:
        """
        try:
            return d_global.request
        except AttributeError:
            warnings.warn(
                'Missing django request object, check you have django_globals.'
                'middleware.Global in middleware_classes and don\'t use this '
                'cache out of django http request scope',
                stacklevel=4
            )

    @property
    def cache(self):
        """
        get cache object stored in django request
        :return: cache (dict) instance
        """
        request = self.request
        cache = getattr(request, self.cache_name, None)
        if not isinstance(cache, collections.MutableMapping):
            cache = self._initialize_cache(request)

        return cache

    def _initialize_cache(self, request):
        """
        Initialize cache in request object
        :return: cache (dict) instance
        """
        cache = {}
        if request:
            setattr(request, self.cache_name, cache)

        return cache

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        """
        Returns the timeout value usable by this backend based upon the provided
        timeout.
        """
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        elif timeout <= 0:
            # ticket 21147 - avoid time.time() related precision issues
            timeout = self.max_timeout
        timeout = min(timeout, self.max_timeout)
        return time.time() + timeout

    def cache_key(self, key, version=None):
        """
        Constructs and validate the key used by all other methods.
        """
        key = self.make_key(key, version=version)
        self.validate_key(key)
        return key

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        """
        key = self.cache_key(key, version=version)
        expiration_time = self.get_backend_timeout(timeout)
        self.cache[key] = CacheItem(value, expiration_time)

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
        self._initialize_cache(self.request)

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

        return super(InRequestCache, self).has_key(key, version)
