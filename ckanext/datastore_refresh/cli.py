# -*- coding: utf-8 -*-

import logging

import ckan.plugins.toolkit as tk
import click

import ckanext.datastore_refresh.helpers as helpers
import ckanext.datastore_refresh.model as model

log = logging.getLogger(__name__)


@click.group(
    name="datastore_config", short_help="Manage datastore_config commands"
)
def datastore_config():
    """Example of group of commands."""
    pass


@datastore_config.command("refresh_dataset_datastore")
@click.argument("frequency")
def refresh_dataset_datastore(frequency):
    """
    Refresh the datastore for a dataset
    """
    click.echo(f"Starting refresh_dataset_datastore for frequency {frequency}")
    if not frequency:
        tk.error_shout("Please provide frequency")

    site_user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": site_user.get("name")}
    datasets = {}
    try:
        datasets = tk.get_action("datastore_refresh_dataset_refresh_list_by_frequency")(
            context, {"frequency": frequency}
        )
    except tk.Invalid as e:
        log.error(e)

    if not datasets:
        click.secho("No datasets with this criteria", fg="yellow")
        return []

    for dataset in datasets["refresh_dataset_datastore"]:
        pkg_id = dataset["package"]["id"]
        pkg_dict = tk.get_action("package_show")(context, {"id": pkg_id})
        click.echo(
            f'Processing dataset {pkg_dict["name"]} with'
            f' {len(pkg_dict["resources"])} resources'
        )

        for res in pkg_dict["resources"]:
            try:
                _submit_resource(pkg_dict, res, context)
            except Exception as e:
                click.secho(e, fg="red")
                click.secho(f'ERROR submitting resource {res["id"]}', fg="red")
                continue

    click.echo(f"Finished refresh_dataset_datastore for frequency {frequency}")


def _submit_resource(dataset, resource, context):
    """resource: resource dictionary"""
    # Copied and modifed from ckan/default/src/ckanext-xloader/ckanext/xloader/cli.py to check for Xloader formats before submitting
    # import here, so that that loggers are setup
    from ckanext.xloader.plugin import XLoaderFormats

    if not XLoaderFormats.is_it_an_xloader_format(resource["format"]):
        click.echo(
            f'Skipping resource {resource["id"]} because format'
            f' "{resource["format"]}" is not configured to be xloadered'
        )
        return
    if resource["url_type"] in ("datapusher", "xloader"):
        click.echo(
            f'Skipping resource {resource["id"]} because url_type'
            f' "{resource["url_type"]}" means resource.url points to the'
            " datastore already, so loading would be circular."
        )
        return

    click.echo(
        f'Submitting /dataset/{dataset["name"]}/resource/{resource["id"]}\n'
        f'url={resource["url"]}\n'
        f'format={resource["format"]}'
    )
    data_dict = {
        "resource_id": resource["id"],
        "ignore_hash": False,
    }

    success = tk.get_action("xloader_submit")(context, data_dict)
    if success:
        click.secho("...ok", fg="green")
    else:
        click.secho("ERROR submitting resource", fg="red")


@datastore_config.command(
    "available_choices", short_help="Shows available choices"
)
def available_choices():
    frequency_options = []
    data = helpers.get_frequency_options()

    for row in data:
        if row["value"] != "0":
            frequency_options.append(row["value"])
    click.secho(f"Available choices: {frequency_options}", fg="green")


def get_commands():
    return [datastore_config]
