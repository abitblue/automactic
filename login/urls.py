from django.urls import path

from . import views

urlpatterns = [
    path('error/', views.Error.as_view(), name='error'),
    path('success/', views.Success.as_view(), name='success'),
    path('login/', views.Index.as_view(), name='login'),
    path('instructions/', views.InstructionsPage.as_view(), name='instructions'),
    path('', views.Homepage.as_view(), name='index'),
]
