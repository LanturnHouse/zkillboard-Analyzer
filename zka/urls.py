from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result', views.analyze, name='result'),
    path('warning', views.analyze, name='warning'),
]