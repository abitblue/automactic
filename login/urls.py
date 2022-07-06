from django.urls import path

from . import views

urlpatterns = [
    path('instructions/', views.Instructions.as_view(), name='instructions'),
    path('', views.Index.as_view(), name='index'),
]