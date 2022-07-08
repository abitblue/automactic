from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    site_header = 'automactic'
    index_title = 'Administrative Portal'

    def index(self, request, extra_context=None):
        return super().index(request, extra_context)
