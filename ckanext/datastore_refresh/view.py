import logging
import ckan.model as model
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

from flask import Blueprint
from flask.views import MethodView

from ckanext.datastore_refresh import helpers

NotFound = toolkit.ObjectNotFound
get_action = toolkit.get_action
h = toolkit.h
render = toolkit.render
log = logging.getLogger(__name__)
datastore_config = Blueprint('datastore_config', __name__)


@datastore_config.before_request
def before_request():
    try:
        context = {
            "model": model, "user": toolkit.g.user, 
            "auth_user_obj": toolkit.g.userobj
        }
        logic.check_access(u'sysadmin', context)
    except logic.NotAuthorized:
        toolkit.base.abort(403, toolkit._(u'Need to be system administrator to administer'))


class DatastoreRefreshConfigView(MethodView):

    def _setup_extra_template_variables(self):
        context = {}
        user = toolkit.g.userobj
        if user:
            context = {u'for_view': True, u'user': user.name, u'auth_user_obj': user}
        #data_dict = {u'user_obj': user, u'include_datasets': True}
        return context

    def _get_context(self):
        return {
            'model': model,
            'session': model.Session,
            'user': toolkit.g.user,
            'auth_user_obj': toolkit.g.userobj
        }

    def get(self, context=None, errors=None, error_summary=None):
        context = self._get_context()

        extra_vars = self._setup_extra_template_variables()
        extra_vars['errors'] = errors
        extra_vars['error_summary'] = error_summary

        return render('admin/datastore_refresh.html', extra_vars=extra_vars)

    def post(self):
        context = self._get_context()
        params = helpers.clean_params(toolkit.request.form)
        if params.get('delete_config'):
            get_action('refresh_dataset_datastore_delete')(context, {'id': params.get('delete_config')})
            h.flash_success(toolkit._("Succesfully deleted configuration"))
            return h.redirect_to('datastore_config.datastore_refresh_config')

        if not params.get('dataset'):
            h.flash_error(toolkit._('Please select dataset'))
            return self.get()

        if params.get('frequency') == '0' or not params.get('frequency'):
            h.flash_error(toolkit._('Please select frequency'))
            return self.get()
        try:
            dataset = get_action('package_show')(context, {'id': params.get('dataset')})
        except NotFound as e:
            h.flash_error(toolkit._(f'Selected dataset {params.get("dataset")} does not exists'))
            return self.get()

        config_dict = {
            "package_id": dataset.get('id'),
            "frequency": params.get('frequency')
        }
        results = get_action('refresh_datastore_dataset_create')(context, config_dict)
        extra_vars = self._setup_extra_template_variables()
        extra_vars["data"] = results
        return h.redirect_to('datastore_config.datastore_refresh_config')


class DatastoreRefreshConfigViewEdit(MethodView):
    def _get_context(self):
        return {
            'model': model,
            'session': model.Session,
            'user': toolkit.g.user,
            'auth_user_obj': toolkit.g.userobj
        }

    def post(self, id):
        context = self._get_context()
        extra_vars = {'id': id}
        params = helpers.clean_params(toolkit.request.form)
        params.update({'id': extra_vars.get('id')})
        get_action('refresh_dataset_datastore_edit_frequency')(context, params)
        return h.redirect_to('datastore_config.datastore_refresh_config')

    def get(self, id):
        context = self._get_context()
        extra_vars = {'id': id}
        data_dict = get_action('refresh_dataset_datastore_show')(context, extra_vars)
        dataset = get_action("package_show")(context, {"id": data_dict["dataset_id"]})

        extra_vars.update({"name": dataset["name"]})
        return render('admin/edit_datastore_refresh_frequency.html', extra_vars=extra_vars)




def register_plugin_rules(blueprint):
    blueprint.add_url_rule('/ckan-admin/datastore-refresh-config',
                           view_func=DatastoreRefreshConfigView.as_view(str('datastore_refresh_config')))
    blueprint.add_url_rule('/ckan-admin/datastore-refresh-config/edit/<id>',
                           view_func=DatastoreRefreshConfigViewEdit.as_view(str('datastore_refresh_config_edit')))


register_plugin_rules(datastore_config)
