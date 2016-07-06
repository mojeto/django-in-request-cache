#!//usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License - full license can be found in LICENSE file.
# Copyright (c) 2016 Jan Nakladal

from __future__ import unicode_literals, absolute_import

import codecs
import os
import re

from setuptools import setup, find_packages


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    'Django>=1.6',
    'django-globals>=0.2',
]


setup(
    name='django-in-request-cache',
    version=find_version('django_in_request_cache', '__init__.py'),
    author='Jan Nakladal',
    author_email='mojeto1@gmail.com',
    url='https://github.com/mojeto/django-in-request-cache',
    description='Django cache stored in django request',
    long_description=read('README.md'),
    setup_requires=['pytest-runner'],
    install_requires=install_requires,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ],
    extras_require={},
    tests_require=[
        'pytest',
        'pytest-django',
    ]
)
