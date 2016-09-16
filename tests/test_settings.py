#!//usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License - full license can be found in LICENSE file.
# Copyright (c) 2016 Jan Nakladal

from __future__ import unicode_literals, absolute_import

from django.conf.global_settings import CACHES as DEFAULT_CACHES

SECRET_KEY = 'test-key'

CACHES = dict(
    DEFAULT_CACHES,
    main_cache={
        'BACKEND': 'tests.test_cache_a_cache.MockCache',
        'LOCATION': 'main_cache',
        'OPTIONS': {
            'TIMEOUT': 200,
        },
    },
    fast_cache={
        'BACKEND': 'tests.test_cache_a_cache.MockCache',
        'LOCATION': 'fast_cache',
        'OPTIONS': {
            'TIMEOUT': 100,
        },
    },
)
