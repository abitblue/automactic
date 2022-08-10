from django.urls import path, include

from . import views

urlpatterns = [
    path('debug/', views.Debug.as_view(), name='debug'),
    path('login/<slug:usertype>', views.Login.as_view(), name='login'),
    path('instructions/', views.Instructions.as_view(), name='instructions'),
    path('success/', views.Success.as_view(), name='success'),
    path('error/', views.Error.as_view(), name='error'),
    path('_internal/bulkuserupload/', views.InternalBulkUserUpload.as_view(), name='internal-bulkuserupload'),
    path('', views.Index.as_view(), name='index'),
]
