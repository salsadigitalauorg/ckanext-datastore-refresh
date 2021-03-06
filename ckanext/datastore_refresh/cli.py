# -*- coding: utf-8 -*-

import click
import ckan.plugins.toolkit as tk

import ckanext.datastore_refresh.model as datavic_model
import ckanext.datastore_refresh.helpers as helpers


@click.group(name=u'datastore_config', short_help=u'Manage datastore_config commands')
def datastore_config():
    """Example of group of commands.
    """
    pass

@datastore_config.command("init_db")
def init_db():
    """Initialise the database tables required for datastore refresh config
    """
    click.secho(u"Initializing Datastore Refresh Config tables", fg=u"green")

    try:
        datavic_model.setup()
    except Exception as e:
        tk.error_shout(str(e))

    click.secho(u"Datastore Refresh Config DB tables are setup", fg=u"green")

@datastore_config.command("refresh_dataset_datastore")
@click.argument(u"frequency")
def refresh_dataset_datastore(frequency):
    """
    Refresh the datastore for a dataset
    """
    
    if not frequency:
        tk.error_shout("Please provide frequency")
    
    site_user = tk.get_action(u'get_site_user')({u'ignore_auth': True}, {})
    
    datasets = tk.get_action('refresh_dataset_datastore_by_frequency')({}, {"frequency": frequency})
    
    if not datasets:
        click.secho("No datasets with this criteria", fg="yellow")

    for dataset in datasets:
        resources = dataset.get('Package').resources
        for res in resources:
            res = tk.get_action('xloader_submit')({"user": site_user, "ignore_auth": True}, {"resource_id": res.id })

def get_commands():
    return [datastore_config]