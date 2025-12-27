# api/middleware.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser

class JWTStrawberryMiddleware:
    def __init__(self):
        self.auth = JWTAuthentication()

    async def __call__(self, request, next):
        user = AnonymousUser()
        header = request.headers.get('authorization')
        if header:
            validated = self.auth.authenticate(request)
            if validated:
                user, _ = validated
        request.user = user
        return await next(request)