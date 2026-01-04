# graphql_gateway/urls.py
from django.contrib import admin
from django.urls import path, re_path
from django.shortcuts import redirect
from api.views import graphql_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", graphql_view),
    re_path(r'^$', lambda request: redirect('/graphql/')),
]