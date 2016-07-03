#!//usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License - full license can be found in LICENSE file.
# Copyright (c) 2016 Jan Nakladal

from __future__ import unicode_literals, absolute_import

import django_globals
import pytest
from django.test import Client
from django_globals.middleware import Global


@pytest.fixture()
def global_request():
    request = {}
    Global().process_request(request)
    return request


def test_global_request_fixture(global_request):
    assert global_request is django_globals.globals.request


def test_cache_in_request(client):
    assert isinstance(client, Client)
