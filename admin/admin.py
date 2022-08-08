from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    site_header = 'automactic'
    index_title = 'Administrative Portal'

    def index(self, *args, **kwargs):
        return super().index(*args, **kwargs)

    def get_app_list(self, request):
        values = super().get_app_list(request)

        # Reverse the login model list to be reverse alphabetical order.
        for app in values:
            if app['app_label'] == 'login':
                app['models'].reverse()
        return values
