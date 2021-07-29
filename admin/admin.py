from django.contrib import admin

from login.forms.user import UserBulkImportForm


class CustomAdminSite(admin.AdminSite):
    site_header = 'automactic'
    index_title = 'Administrative Portal'
    index_template = 'admin_index.html'

    def index(self, request, extra_context=None):
        extra_context = {'bulkImportForm': UserBulkImportForm()}
        return super().index(request, extra_context)


admin_site = CustomAdminSite()
