from django.shortcuts import render
from strawberry.django.views import GraphQLView
from .schema import schema
from .middleware import JWTStrawberryMiddleware

class CustomGraphQLView(GraphQLView):
    def get_middleware(self):
        return [JWTStrawberryMiddleware()]

graphql_view = GraphQLView.as_view(schema=schema)

# Create your views here.
