from django.urls import path
import django.contrib.auth.urls

from . import views

app_name = "clusters"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("manage/", views.ManageView.as_view(), name="manage"),
    path("users/<int:user_id>", views.UserView.as_view(), name="users"),
]
