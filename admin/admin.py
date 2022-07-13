from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    site_header = 'automactic'
    index_title = 'Administrative Portal'

    def index(self, *args, **kwargs):
        return super().index(*args, **kwargs)
