# config/middleware.py
import time
from django.http import JsonResponse

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # فحص صحة سريع لـ UptimeRobot
        if request.path == '/health/' or request.path == '/health':
            start_time = time.time()
            
            # التحقق من صحة قاعدة البيانات
            from django.db import connection
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    db_healthy = True
            except:
                db_healthy = False
            
            response_time = (time.time() - start_time) * 1000  # بالميلي ثانية
            
            return JsonResponse({
                'status': 'healthy' if db_healthy else 'unhealthy',
                'database': 'connected' if db_healthy else 'disconnected',
                'timestamp': time.time(),
                'response_time_ms': round(response_time, 2),
                'service': 'Django Files Store API',
                'uptime_robot': 'enabled'
            })
        
        return self.get_response(request)