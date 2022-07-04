import logging

import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from flask.views import MethodView

from ckan.lib.navl.dictization_functions import unflatten
from ckan.logic import clean_dict, parse_params, tuplize_dict

NotFound = toolkit.ObjectNotFound
get_action = toolkit.get_action
h = toolkit.h
render = toolkit.render
log = logging.getLogger(__name__)
datastore_refresh = Blueprint("datastore_refresh", __name__)


def get_blueprints():
    return [datastore_refresh]


def clean_params(params):
    return clean_dict(unflatten(tuplize_dict(parse_params(params))))


@datastore_refresh.before_request
def before_request():
    try:
        context = {
            "model": model,
            "user": toolkit.g.user,
            "auth_user_obj": toolkit.g.userobj,
        }
        logic.check_access("sysadmin", context)
    except logic.NotAuthorized:
        toolkit.base.abort(
            403, toolkit._("Need to be system administrator to administer")
        )


class DatastoreRefreshConfigView(MethodView):
    def _setup_extra_template_variables(self):
        context = {}
        user = toolkit.g.userobj
        if user:
            context = {
                "for_view": True,
                "user": user.name,
                "auth_user_obj": user,
            }
        # data_dict = {u'user_obj': user, u'include_datasets': True}
        return context

    def _get_context(self):
        return {
            "model": model,
            "session": model.Session,
            "user": toolkit.g.user,
            "auth_user_obj": toolkit.g.userobj,
        }

    def get(self):
        extra_vars = self._setup_extra_template_variables()
        return render("admin/datastore_refresh.html", extra_vars=extra_vars)

    def post(self):
        context = self._get_context()
        params = clean_params(toolkit.request.form)
        if params.get("delete_config"):
            get_action("datastore_refresh_dataset_refresh_delete")(
                context, {"id": params.get("delete_config")}
            )
            h.flash_success(toolkit._("Succesfully deleted configuration"))
            return h.redirect_to("datastore_refresh.datastore_refresh_config")

        if not params.get("dataset"):
            h.flash_error(toolkit._("Please select dataset"))
            return self.get()

        if params.get("frequency") == "0" or not params.get("frequency"):
            h.flash_error(toolkit._("Please select frequency"))
            return self.get()
        try:
            dataset = get_action("package_show")(
                context, {"id": params.get("dataset")}
            )
        except NotFound as e:
            h.flash_error(
                toolkit._(
                    f'Selected dataset {params.get("dataset")} does not exists'
                )
            )
            return self.get()

        config_dict = {
            "package_id": dataset.get("id"),
            "frequency": params.get("frequency"),
        }
        results = get_action("datastore_refresh_dataset_refresh_create")(
            context, config_dict
        )
        extra_vars = self._setup_extra_template_variables()
        extra_vars["data"] = results
        return h.redirect_to("datastore_refresh.datastore_refresh_config")


def register_plugin_rules(blueprint):
    blueprint.add_url_rule(
        "/ckan-admin/datastore-refresh-config",
        view_func=DatastoreRefreshConfigView.as_view(
            str("datastore_refresh_config")
        ),
    )


register_plugin_rules(datastore_refresh)
