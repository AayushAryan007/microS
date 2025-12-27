from django.shortcuts import render
from strawberry.django.views import AsyncGraphQLView
from .schema import schema
from .middleware import JWTStrawberryMiddleware

class CustomGraphQLView(AsyncGraphQLView):
    def get_middleware(self):
        return [JWTStrawberryMiddleware()]

# Create your views here.
