from .views import render, serv, Serveur
from django.urls import path

urlpatterns = [
    path("api/command/add", serv.api_add),
    path("api/command/list", serv.api_list),
    path("api/command/search/<str:query>", serv.api_search),
    path("", serv.index),
]