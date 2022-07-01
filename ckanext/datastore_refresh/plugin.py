import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.xloader.interfaces as xloader_interfaces

from . import cli, helpers, view
from .logic import auth, action


log = logging.getLogger(__name__)


class DatastoreRefreshPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(xloader_interfaces.IXloader, inherit=True)

    # ITemplateHelpers
    def get_helpers(self):
        return {
            "get_frequency_options": helpers.get_frequency_options,
            "get_datastore_refresh_configs": helpers.get_datastore_refresh_configs,
            "get_datasore_refresh_config_option": helpers.get_datasore_refresh_config_option,
            "time_ago_from_datetime": helpers.time_ago_from_datetime,
        }

    # IActions
    def get_actions(self):
        return action.get_actions()

    # IAuthFunctions
    def get_auth_functions(self):
        return auth.get_auth_functions()

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "datastore_refresh")
        # Add a new ckan-admin tabs for our extension
        toolkit.add_ckan_admin_tab(
            toolkit.config,
            "datastore_config.datastore_refresh_config",
            "Datastore refresh",
            config_var="ckan.admin_tabs",
        )

    # IClick
    def get_commands(self):
        return cli.get_commands()

    # IBlueprint
    def get_blueprint(self):
        return view.datastore_config

    # IXLoader
    def after_upload(self, context, resource_dict, dataset_dict):
        helpers.purge_section_cache(context, resource_dict, dataset_dict)
