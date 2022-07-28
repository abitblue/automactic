from django.urls import path, include

from . import views

urlpatterns = [
    path('debug/', views.Debug.as_view(), name='debug'),

    path('kiosk/', include([
        path('login/<slug:usertype>', views.Login.as_view(), kwargs={'kiosk': True}, name='kiosk_login'),
        path('', views.Index.as_view(), kwargs={'kiosk': True}, name='kiosk_index'),
    ])),

    path('login/<slug:usertype>', views.Login.as_view(), name='login'),
    path('instructions/', views.Instructions.as_view(), name='instructions'),
    path('success/', views.Success.as_view(), name='success'),
    path('error/', views.Error.as_view(), name='error'),
    path('', views.Index.as_view(), name='index'),
]
