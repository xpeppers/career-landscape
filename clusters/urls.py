from django.urls import path

from . import views

app_name = "clusters"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("uploadFile/", views.uploadFile, name='uploadFile'),
]
