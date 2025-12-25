"""
URL configuration for inventory_core project.

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
from .views import InventoryView, EditProductView, DeleteProductView, refresh_order_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', InventoryView.as_view(), name='inventory_index'),
    path('edit/<uuid:pk>/', EditProductView.as_view(), name='edit_product'),
    path('delete/<uuid:pk>/', DeleteProductView.as_view(), name='delete_product'),
    path('refresh-order-page/', refresh_order_page, name='refresh_order_page'),
]
