import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


from ckanext.datavic_admin import actions, helpers, cli, view

class DatavicAdminPlugin(plugins.SingletonPlugin):
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions)
    p.implements(p.IConfigurer)
    p.implements(p.IClick)
    p.implements(p.IBlueprint)

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_frequency_options': helpers.get_frequency_options,
            'get_datastore_refresh_configs': helpers.get_datastore_refresh_configs,
            'get_datasore_refresh_config_option': helpers.get_datasore_refresh_config_option,
        }

    # IActions
    def get_actions(self):
        return {
            'refresh_datastore_dataset_create': actions.refresh_datastore_dataset_create,
            'refresh_dataset_datastore_list': actions.refresh_dataset_datastore_list,
            'refresh_dataset_datastore_delete': actions.refresh_dataset_datastore_delete,
            'refresh_dataset_datastore_by_frequency': actions.refresh_dataset_datastore_by_frequency
        }

        # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "datavic_admin")
        # Add a new ckan-admin tabs for our extension
        toolkit.add_ckan_admin_tab(
            config,
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

    
