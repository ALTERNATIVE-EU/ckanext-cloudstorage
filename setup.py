#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ckanext-cloudstorage',
    version='0.1.1',
    description='Cloud storage for CKAN',
    classifiers=[],
    keywords='',
    author='Tyler Kennedy',
    author_email='tk@tkte.ch',
    url='http://github.com/open-data/ckanext-cloudstorage',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'apache-libcloud==3.6.0',
        'ckanapi>=1.0,<5',
        'google-auth==2.11.0',
        'six==1.16.0',
        'routes==2.5.1',
        'cryptography==37.0.4'
    ],
    entry_points=(
        """
        [ckan.plugins]
        cloudstorage=ckanext.cloudstorage.plugin:CloudStoragePlugin

        [paste.paster_command]
        cloudstorage=ckanext.cloudstorage.cli:PasterCommand
        """
    ),
)
