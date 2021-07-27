from django.urls import path

from . import views

urlpatterns = [
    path('guestpasswd/', views.InternalGuestPasswd.as_view(), name='internal-guestpasswd'),
    path('bulkuserupload/', views.InternalBulkUserUpload.as_view(), name='internal-bulkuserupload'),
    path('debug/', views.Debug.as_view(), name='debug'),
]