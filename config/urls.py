# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse
from . import views  

def home_api(request):
    return JsonResponse({
        'message': '🚀 مرحباً في متجر الملفات التقنية!',
        'endpoints': {
            'login': '/api/v1/token/',
            'products': '/api/v1/products/',
            'sales': '/api/v1/sales/',
            'notifications': '/api/v1/notifications/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('api/', home_api, name='api-home'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('accounts.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/sales/', include('sales.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     # UptimeRobot endpoints
    path('health/', views.health_check, name='health-check'),
    path('health/simple/', views.simple_health, name='simple-health'),  
    path('ping/', views.uptime_robot_ping, name='uptime-ping'),
    path('api/health/', views.health_check, name='api-health-check'),
]