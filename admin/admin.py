from django.contrib import admin

from login.forms import UserBulkImportForm


class CustomAdminSite(admin.AdminSite):
    site_header = 'automactic'
    index_title = 'Administrative Portal'
    index_template = 'admin/admin_index.html'

    def index(self, request, extra_context=None):
        extra_context = {'bulkImportForm': UserBulkImportForm()}
        return super().index(request, extra_context)

    def get_app_list(self, request):
        values = super().get_app_list(request)

        # Reverse the login model list to be reverse alphabetical order.
        for app in values:
            if app['app_label'] == 'login':
                app['models'].reverse()
        return values
