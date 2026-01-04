from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, authenticate, login as django_login, logout as django_logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.http import require_http_methods, require_POST
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    users = list(User.objects.values('id', 'name', 'email'))
    return JsonResponse(users, safe=False)

@csrf_exempt
@require_POST
def signup(request):
    data = json.loads(request.body)
    name = data['name']
    email = data['email']
    password = data['password']
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already exists'}, status=400)
    user = User.objects.create_user(email=email, name=name, password=password)
    return JsonResponse({'message': 'User created', 'user_id': str(user.id)})

@csrf_exempt
@require_POST
def signin(request):
    data = json.loads(request.body)
    email = data['email']
    password = data['password']
    user = authenticate(request, email=email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': str(user.id),
            'name': user.name,
            'email': user.email,
        })
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        try:
            user = User.objects.get(name=name)
            user = authenticate(request, email=user.email, password=password)
        except User.DoesNotExist:
            user = None
        if user is not None:
            django_login(request, user)
            refresh = RefreshToken.for_user(user)
            request.session['jwt_token'] = str(refresh.access_token)
            return redirect('landing')  # Redirect to landing page after login
        else:
            return render(request, "user_core/login.html", {"error": "Invalid credentials"})
    return render(request, "user_core/login.html")

@require_http_methods(["GET", "POST"])
def signup_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(email=email).exists():
            return render(request, "user_core/signup.html", {"error": "Email already exists"})
        user = User.objects.create_user(email=email, name=name, password=password)
        return redirect('login_page')
    return render(request, "user_core/signup.html")

def landing(request):
    if not request.user.is_authenticated or 'jwt_token' not in request.session:
        return redirect('login_page')
    return render(request, "user_core/landing.html", {
        "name": request.user.name,
        "email": request.user.email,
        "user_id": request.user.id,
        "token": request.session['jwt_token'],
    })

@require_http_methods(["POST"])
def logout(request):
    django_logout(request)
    request.session.flush()
    return redirect('login_page')