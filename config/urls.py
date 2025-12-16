from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def home(request):
    return JsonResponse({'status': 'ok', 'service': 'Django API'})

def health(request):
    return JsonResponse({'status': 'healthy', 'service': 'Django Health Check'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('health/', health, name='health'),
]
