"""
health check views for Django application
"""

import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import os
import shutil


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """فحص صحة شامل"""
    checks = {}
    
    # 1. فحص قاعدة البيانات
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        checks['database'] = {
            'status': 'unhealthy',
            'error': str(e)[:100]
        }
    
    # 2. فحص القرص (بدون psutil)
    try:
        disk = shutil.disk_usage("/")
        disk_percent = (disk.used / disk.total * 100) if disk.total > 0 else 0
        
        checks['disk'] = {
            'status': 'healthy' if disk_percent < 80 else 'warning',
            'percent': round(disk_percent, 1),
            'free_gb': round(disk.free / (1024**3), 2),
            'total_gb': round(disk.total / (1024**3), 2)
        }
    except Exception as e:
        checks['disk'] = {
            'status': 'unknown',
            'error': str(e)[:100]
        }
    
    # 3. الذاكرة (مشروطة بتوفر psutil)
    try:
        import psutil
        memory = psutil.virtual_memory()
        checks['memory'] = {
            'status': 'healthy' if memory.percent < 90 else 'warning',
            'percent': round(memory.percent, 1),
            'available_gb': round(memory.available / (1024**3), 2)
        }
    except ImportError:
        checks['memory'] = {
            'status': 'info',
            'message': 'psutil not installed, memory check skipped'
        }
    except Exception as e:
        checks['memory'] = {
            'status': 'unknown',
            'error': str(e)[:100]
        }
    
    # 4. تحديد الحالة العامة
    has_critical = any(
        check.get('status') == 'unhealthy' 
        for check in checks.values()
    )
    
    status_code = 200 if not has_critical else 503
    overall_status = 'healthy' if not has_critical else 'unhealthy'
    
    response = {
        'status': overall_status,
        'checks': checks,
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'service': 'Technical Files Store API',
        'version': '1.0.0',
        'environment': os.environ.get('DJANGO_ENV', 'production')
    }
    
    return JsonResponse(response, status=status_code)


@csrf_exempt
@require_http_methods(["GET"])
def simple_health(request):
    """فحص صحة خفيف"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'ok',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'service': 'Django API'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': 'Database connection failed',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def disk_analysis(request):
    """تحليل مساحة القرص"""
    try:
        disk = shutil.disk_usage("/")
        total_gb = disk.total / (1024**3)
        used_gb = disk.used / (1024**3)
        free_gb = disk.free / (1024**3)
        percent = (used_gb / total_gb * 100) if total_gb > 0 else 0
        
        if percent > 90:
            status = 'critical'
            recommendation = 'إخلاء مساحة فوراً'
        elif percent > 80:
            status = 'warning'
            recommendation = 'توصية: تنظيف الملفات المؤقتة'
        else:
            status = 'healthy'
            recommendation = 'حالة جيدة'
        
        return JsonResponse({
            'disk': {
                'total_gb': round(total_gb, 2),
                'used_gb': round(used_gb, 2),
                'free_gb': round(free_gb, 2),
                'percent': round(percent, 1),
                'status': status
            },
            'recommendation': recommendation,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Disk analysis failed',
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, status=500)
