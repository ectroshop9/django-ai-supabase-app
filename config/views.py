from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import datetime

def index_page(request):
    """عرض الصفحة الرئيسية الجميلة"""
    base_url = request.build_absolute_uri('/')
    
    context = {
        'base_url': base_url,
        'current_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'project_name': 'نظام بيع الملفات التقنية',
        'version': '1.0.0',
    }
    
    return render(request, 'index.html', context)

def api_home(request):
    """الصفحة الرئيسية للـ API (JSON)"""
    base_url = request.build_absolute_uri('/')
    
    return JsonResponse({
        'project': 'نظام بيع الملفات التقنية',
        'version': '1.0.0',
        'status': '🟢 نشط',
        'timestamp': datetime.datetime.now().isoformat(),
        'endpoints': {
            'home_html': base_url,
            'admin': f'{base_url}admin/',
            'api_root': f'{base_url}api/v1/',
            'api_status': f'{base_url}api/v1/status/',
            'api_token': f'{base_url}api/v1/token/',
            'api_token_refresh': f'{base_url}api/v1/token/refresh/',
        },
        'note': 'استخدم POST /api/v1/token/ للحصول على JWT'
    })