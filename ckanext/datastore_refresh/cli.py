# -*- coding: utf-8 -*-

import json
from logging import getLogger
import click
import logging
import ckan.plugins.toolkit as tk
import ckan.model as model

from ckan.common import config

import ckanext.datastore_refresh.model as datavic_model
import ckanext.datastore_refresh.choices as choices


log = logging.getLogger(__name__)


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
    click.echo(f"Starting refresh_dataset_datastore for frequency {frequency}")
    if not frequency:
        tk.error_shout("Please provide frequency")

    site_user = tk.get_action(u'get_site_user')({u'ignore_auth': True}, {})
    datasets = {}
    try:
        datasets = tk.get_action('refresh_dataset_datastore_by_frequency')({}, {"frequency": frequency})
    except tk.Invalid as e:
        log.error(e)

    if not datasets:
        click.secho("No datasets with this criteria", fg="yellow")
        return []

    for dataset in datasets["refresh_dataset_datastore"]:
        pkg_id = dataset['package']['id']
        pkg_dict = tk.get_action('package_show')({"model": model}, {'id': pkg_id})
        click.echo(f'Processing dataset {pkg_dict["name"]} with {len(pkg_dict["resources"])} resources')

        for res in pkg_dict['resources']:
            try:
                _submit_resource(pkg_dict, res, site_user)
            except Exception as e:
                click.secho(e, fg="red")
                click.secho(f'ERROR submitting resource {res["id"]}', fg="red")
                continue

    click.echo(f"Finished refresh_dataset_datastore for frequency {frequency}")


def _submit_resource(dataset, resource, user):
    '''resource: resource dictionary
    '''
    # Copied and modifed from ckan/default/src/ckanext-xloader/ckanext/xloader/cli.py to check for Xloader formats before submitting
    # import here, so that that loggers are setup
    from ckanext.xloader.plugin import XLoaderFormats

    if not XLoaderFormats.is_it_an_xloader_format(resource["format"]):
        click.echo(f'Skipping resource {resource["id"]} because format "{resource["format"]}" is not configured to be xloadered')
        return
    if resource["url_type"] in ('datapusher', 'xloader'):
        click.echo(f'Skipping resource {resource["id"]} because url_type "{resource["url_type"]}" '
                   'means resource.url points to the datastore '
                   'already, so loading would be circular.')
        return

    click.echo(f'Submitting /dataset/{dataset["name"]}/resource/{resource["id"]}\n'
               f'url={resource["url"]}\n'
               f'format={resource["format"]}')
    data_dict = {
        'resource_id': resource["id"],
        'ignore_hash': False,
    }

    success = tk.get_action('xloader_submit')({'user': user['name'], "ignore_auth": True}, data_dict)
    if success:
        click.secho('...ok', fg="green")
    else:
        click.secho('ERROR submitting resource', fg="red")


@datastore_config.command("available_choices", short_help="Shows available choices")
def available_choices():
    _choices = []
    data = choices.load_options()

    for row in data:
        if row['value'] != '0':
            _choices.append(row['value'])
    click.secho(f'Available choices: {_choices}', fg="green")


def get_commands():
    return [datastore_config]
