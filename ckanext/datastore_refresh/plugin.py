import requests

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.xloader.interfaces as xloader_interfaces 
from ckanext.datastore_refresh import actions, helpers, cli, view

class DatastoreRefreshPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(xloader_interfaces.IXloader)

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_frequency_options': helpers.get_frequency_options,
            'get_datastore_refresh_configs': helpers.get_datastore_refresh_configs,
            'get_datasore_refresh_config_option': helpers.get_datasore_refresh_config_option,
            'time_ago_from_datetime': helpers.time_ago_from_datetime,
        }

    # IActions
    def get_actions(self):
        return {
            'refresh_datastore_dataset_create': actions.refresh_datastore_dataset_create,
            'refresh_dataset_datastore_list': actions.refresh_dataset_datastore_list,
            'refresh_dataset_datastore_delete': actions.refresh_dataset_datastore_delete,
            'refresh_dataset_datastore_by_frequency': actions.refresh_dataset_datastore_by_frequency,
            'refresh_datastore_dataset_update': actions.refresh_datastore_dataset_update,
        }

        # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "datastore_refresh")
        # Add a new ckan-admin tabs for our extension
        toolkit.add_ckan_admin_tab(
            toolkit.config,
            'datastore_config.datastore_refresh_config',
            'Datastore refresh',
            config_var='ckan.admin_tabs'
        )

    # IClick
    def get_commands(self):
        return cli.get_commands()

    # IBlueprint
    def get_blueprint(self):
        return view.datastore_config

    # IXLoader
    def can_upload(self, resource_id):
        return True

    def after_upload(self, context, resource_dict, dataset_dict):
        package_id = dataset_dict.get('id')
        rdd = toolkit.get_action('refresh_datastore_dataset_update')(context, {'package_id': package_id})
        if rdd and toolkit.config.get('ckanext.datastore_refresh.refresh_on_upload', False):
            # Ping the CDN for COVID cache 
            requests.get(toolkit.config.get('ckanext.datastore_refresh.refresh_on_upload'))

    
