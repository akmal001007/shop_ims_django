from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('admin/')),
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),  # ✅ This includes all your app routes
]
