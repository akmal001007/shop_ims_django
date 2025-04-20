from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),             # <-- this enables the admin
    path('api/', include('inventory.urls')),         # your inventory API
]
