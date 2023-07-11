from ast import literal_eval
import os
import json

from ckan.common import config


# ckanext.cloudstorage.driver
# 
# S3, GOOGLE_STORAGE, AZURE_BLOBS
# 
DRIVER = config.get('ckanext.cloudstorage.driver')

# server_url = config.get('ckanext.keycloak.server_url')
#         if not server_url:
#             raise RuntimeError(missing_param.format('ckanext.keycloak.server_url'))


# ckanext.cloudstorage.container_name
# 
# Bucket Name
# 
CONTAINER_NAME = config.get('ckanext.cloudstorage.container_name')


# ckanext.cloudstorage.driver_options
# 
# AWS: Access Key ID, Secret Access Key, Bucket Region
# 
# GOOGLE: Client Email, Private Key
# 
# AZURE: Storage Account, Access Key
# 
# format: {"key": "key", "secret": "secret", "region": "region"}
# 
DRIVER_OPTIONS = literal_eval(config['ckanext.cloudstorage.driver_options'])


# Path to Google credentials JSON file - needed only when using Google
GOOGLE_CREDS = config.get('ckanext.cloudstorage.google_creds')