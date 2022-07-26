from django.urls import path

from . import views

urlpatterns = [
    path('instructions/', views.Instructions.as_view(), name='instructions'),
    path('students/', views.Students.as_view(), name='students'),
    path('teachers/', views.Teachers.as_view(), name='teachers'),
    path('success/', views.Success.as_view(), name='success'),
    path('error/', views.Error.as_view(), name='error'),
    path('debug/', views.Debug.as_view(), name='debug'),
    path('', views.Index.as_view(), name='index'),
]
