# graphql_gateway/urls.py
from django.urls import path
from api.views import CustomGraphQLView

urlpatterns = [
    path("graphql/", CustomGraphQLView.as_view(schema=schema)),
]