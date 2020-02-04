from django.urls import path
import django.contrib.auth.urls

from . import views

app_name = "clusters"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("manage/", views.ManageView.as_view(), name="manage"),
]
