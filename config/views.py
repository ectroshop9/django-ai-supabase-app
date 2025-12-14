# config/views.py - النسخة المعدلة
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import psutil
import time
from django.db import connection
import datetime



@require_GET
def health_check(request):
    """فحص مفصل لصحة النظام"""
    checks = {}
    start_time = time.time()
    
    # 1. فحص قاعدة البيانات
    db_start = time.time()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_time = (time.time() - db_start) * 1000
        checks['database'] = {
            'status': 'healthy',
            'response_time_ms': round(db_time, 2)
        }
    except Exception as e:
        checks['database'] = {
            'status': 'unhealthy',
            'error': str(e)[:100]  # تقليل طول الرسالة
        }
    
    # 2. فحص الذاكرة (إذا كان psutil متاحاً)
    try:
        memory = psutil.virtual_memory()
        checks['memory'] = {
            'status': 'healthy' if memory.percent < 90 else 'warning',
            'percent': round(memory.percent, 1),
            'available_gb': round(memory.available / (1024**3), 2)
        }
    except Exception:
        checks['memory'] = {'status': 'unknown', 'note': 'psutil not available'}
    
    # 3. فحص القرص
    try:
        disk = psutil.disk_usage('/')
        checks['disk'] = {
            'status': 'healthy' if disk.percent < 85 else 'warning',
            'percent': round(disk.percent, 1),
            'free_gb': round(disk.free / (1024**3), 2)
        }
    except Exception:
        checks['disk'] = {'status': 'unknown', 'note': 'disk check failed'}
    
    # 4. فحص وقت الاستجابة الكلي
    total_time = (time.time() - start_time) * 1000
    
    # تحديد الحالة العامة
    all_healthy = all(
        check.get('status') in ['healthy', 'warning', 'unknown'] 
        for check in checks.values()
    )
    
    status_code = 200 if all_healthy else 503
    status_text = 'healthy' if all_healthy else 'unhealthy'
    
    response = JsonResponse({
        'status': status_text,
        'checks': checks,
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'Technical Files Store',
        'response_time_ms': round(total_time, 2),
        'uptime_robot': 'ready'
    }, status=status_code)
    
    response['X-Response-Time'] = f'{total_time:.2f}ms'
    response['X-Health-Check'] = 'true'
    return response

@require_GET
def uptime_robot_ping(request):
    """Endpoint خاص بـ UptimeRobot"""
    return JsonResponse({
        'status': 'pong',
        'service': 'Django Files Store',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0',
        'message': '✅ UptimeRobot monitoring is active'
    })

@require_GET
def simple_health(request):
    """فحص صحة بسيط"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({
            'status': 'ok',
            'database': 'connected',
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'database': 'disconnected',
            'error': str(e)[:100]
        }, status=503)