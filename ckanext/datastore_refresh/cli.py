# -*- coding: utf-8 -*-

import json
import click
import ckan.plugins.toolkit as tk
import ckan.model as model

from ckan.common import config

import ckanext.datastore_refresh.model as datavic_model


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
    if not frequency or frequency == '0':
        tk.error_shout("Please provide frequency")

    site_user = tk.get_action(u'get_site_user')({u'ignore_auth': True}, {})
    datasets = tk.get_action('refresh_dataset_datastore_by_frequency')({"model": model}, {"frequency": frequency})

    if not datasets:
        click.secho("No datasets with this criteria", fg="yellow")
        return []

    for dataset in datasets['refresh_dataset_datastore']:
        pkg_id = dataset['package']['id']
        pkg_dict = tk.get_action('package_show')({"model": model}, {'id': pkg_id})
        for res in pkg_dict['resources']:
            res = tk.get_action('xloader_submit')({"user": site_user, "ignore_auth": True}, {"resource_id": res['id'] })

@datastore_config.command("available_choices", short_help="Shows available choices")
def available_choices():
    frequency_options = config.get('ckanext.datastore_refresh.frequency_options', {})
    if not frequency_options:
        click.secho('No frequency options are configured', fg="red")
        return

    choices = []
    with open(frequency_options) as f:
        json_choices = f.read()
        json_choices = json.loads(json_choices)

        for row in json_choices['frequency_options']:
            if row['value'] != '0':
                choices.append(row['value'])
    click.secho(f'Available choices: {choices}', fg="green")

def get_commands():
    return [datastore_config]