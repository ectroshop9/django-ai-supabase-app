# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # أضف هذا
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse

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
]