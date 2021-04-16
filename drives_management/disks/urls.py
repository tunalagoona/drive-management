from django.urls import path

from . import views


urlpatterns = [
    path('', views.PartitionsView.as_view(), name='disks'),
]
