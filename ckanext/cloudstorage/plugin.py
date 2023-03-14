#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ckan import plugins
from routes.mapper import SubMapper
import os.path
from ckanext.cloudstorage import storage
from ckanext.cloudstorage import helpers
import ckanext.cloudstorage.logic.action.multipart as m_action
import ckanext.cloudstorage.logic.auth.multipart as m_auth
from flask import Blueprint
from flask import g
from flask import render_template_string
from ckan import logic, model
from ckan.lib import base, uploader

def resource_download(id, resource_id, filename=None):
    context = {
        'model': model,
        'session': model.Session,
        'user': g.user or g.author,
        'auth_user_obj': g.userobj
    }

    try:
        resource = logic.get_action('resource_show')(
            context,
            {
                'id': resource_id
            }
        )
    except logic.NotFound:
        base.abort(404, ('Resource not found'))
    except logic.NotAuthorized:
        base.abort(401, ('Unauthorized to read resource {0}'.format(id)))

    # This isn't a file upload, so either redirect to the source
    # (if available) or error out.
    if resource.get('url_type') != 'upload':
        url = resource.get('url')
        if not url:
            base.abort(404, ('No download is available'))
        h.redirect_to(url)

    if filename is None:
        # No filename was provided so we'll try to get one from the url.
        filename = os.path.basename(resource['url'])

    upload = uploader.get_resource_uploader(resource)

    # if the client requests with a Content-Type header (e.g. Text preview)
    # we have to add the header to the signature
    try:
        content_type = getattr(g, "content_type", 'text/plain')
    except AttributeError:
        content_type = None
    uploaded_url = upload.get_url_from_filename(resource['id'], filename,
                                                content_type=content_type)

    # The uploaded file is missing for some reason, such as the
    # provider being down.
    if uploaded_url is None:
        base.abort(404, ('No download is available'))

    # Return HTML to redirect to url
    html = u'''<!DOCTYPE html>
<html>
    <head>
        <title>Download - {{ g.site_title }}</title>
    </head>
    <body>
    <meta http-equiv="Refresh" content="0; url='link'" />
    </body>
</html>'''
    html = html.replace("link", uploaded_url)
    return render_template_string(html)

class CloudStoragePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IUploader)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IBlueprint)

    #IBlueprint

    def get_blueprint(self):
        '''Return a Flask Blueprint object to be registered by the app.'''

        # Create Blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'
        # Add plugin url rules to Blueprint object
        rules = [
            ('/dataset/<id>/resource/<resource_id>/download/<filename>', '', resource_download),
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint

    # IConfigurer

    def update_config(self, config):
        plugins.toolkit.add_template_directory(config, 'templates')
        plugins.toolkit.add_resource('assets', 'cloudstorage-js')

    # ITemplateHelpers

    def get_helpers(self):
        return dict(
            cloudstorage_use_secure_urls=helpers.use_secure_urls
        )

    def configure(self, config):

        required_keys = (
            'ckanext.cloudstorage.driver',
            # 'ckanext.cloudstorage.driver_options',
            'ckanext.cloudstorage.container_name'
        )

        for rk in required_keys:
            if config.get(rk) is None:
                raise RuntimeError(
                    'Required configuration option {0} not found.'.format(
                        rk
                    )
                )

    def get_resource_uploader(self, data_dict):
        # We provide a custom Resource uploader.
        return storage.ResourceCloudStorage(data_dict)

    def get_uploader(self, upload_to, old_filename=None):
        # We don't provide misc-file storage (group images for example)
        # Returning None here will use the default Uploader.
        return None

    # IActions

    def get_actions(self):
        return {
            'cloudstorage_initiate_multipart': m_action.initiate_multipart,
            'cloudstorage_upload_multipart': m_action.upload_multipart,
            'cloudstorage_finish_multipart': m_action.finish_multipart,
            'cloudstorage_abort_multipart': m_action.abort_multipart,
            'cloudstorage_check_multipart': m_action.check_multipart,
            'cloudstorage_clean_multipart': m_action.clean_multipart,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'cloudstorage_initiate_multipart': m_auth.initiate_multipart,
            'cloudstorage_upload_multipart': m_auth.upload_multipart,
            'cloudstorage_finish_multipart': m_auth.finish_multipart,
            'cloudstorage_abort_multipart': m_auth.abort_multipart,
            'cloudstorage_check_multipart': m_auth.check_multipart,
            'cloudstorage_clean_multipart': m_auth.clean_multipart,
        }

    # IResourceController

    def before_delete(self, context, resource, resources):
        # let's get all info about our resource. It somewhere in resources
        # but if there is some possibility that it isn't(magic?) we have
        # `else` clause

        for res in resources:
            if res['id'] == resource['id']:
                break
        else:
            return
        # just ignore simple links
        if res['url_type'] != 'upload':
            return

        # we don't want to change original item from resources, just in case
        # someone will use it in another `before_delete`. So, let's copy it
        # and add `clear_upload` flag
        res_dict = dict(res.items())
        res_dict['clear_upload'] = True

        uploader = self.get_resource_uploader(res_dict)

        # to be on the safe side, let's check existence of container
        container = getattr(uploader, 'container', None)
        if container is None:
            return

        # and now uploader removes our file.
        uploader.upload(resource['id'])

        # and all other files linked to this resource
        if not uploader.leave_files:
            upload_path = os.path.dirname(
                uploader.path_from_filename(
                    resource['id'],
                    'fake-name'
                )
            )

            for old_file in uploader.container.iterate_objects():
                if old_file.name.startswith(upload_path):
                    old_file.delete()
