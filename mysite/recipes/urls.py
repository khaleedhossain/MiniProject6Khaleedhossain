# INF601 - Advanced Programming in Python
# Khaleed Hossain
# Mini Project 6

from django.urls import path

from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.index, name="index"),
    path("mine/", views.mine, name="mine"),
    path("<int:pk>/", views.detail, name="detail"),
    path("create/", views.create, name="create"),
    path("<int:pk>/update/", views.update, name="update"),
    path("<int:pk>/delete/", views.delete, name="delete"),
]
