"""
URL configuration for order_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import order_create, order_success

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', order_create, name='order_create'),  # root now shows create order form
    path('create-order/', order_create, name='order_create_alt'),  # optional: keep alternate route
    path('order-success/', order_success, name='order_success'),
]
