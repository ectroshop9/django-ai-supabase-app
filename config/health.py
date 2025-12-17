"""
Health check endpoints for Fly.io monitoring
"""

from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError
import psutil
import os


class HealthCheckView(View):
    """
    Comprehensive health check endpoint for Fly.io
    Returns 200 if all systems are operational
    """
    
    def get(self, request, *args, **kwargs):
        checks = {
            "status": "checking",
            "service": os.environ.get('FLY_APP_NAME', 'django-app'),
            "environment": "production" if not DEBUG else "development",
            "checks": {}
        }
        
        # 1. Database Check
        try:
            db_conn = connections['default']
            db_conn.cursor()
            checks["checks"]["database"] = {
                "status": "healthy",
                "type": db_conn.vendor
            }
        except OperationalError as e:
            checks["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 2. Cache Check
        try:
            cache.set('health_check', 'ok', 5)
            cache_result = cache.get('health_check')
            checks["checks"]["cache"] = {
                "status": "healthy" if cache_result == 'ok' else "unhealthy",
                "backend": cache.__class__.__name__
            }
        except Exception as e:
            checks["checks"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 3. Disk Usage Check
        try:
            disk_usage = psutil.disk_usage('/')
            checks["checks"]["disk"] = {
                "status": "healthy" if disk_usage.percent < 90 else "warning",
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "percent": disk_usage.percent
            }
        except Exception as e:
            checks["checks"]["disk"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 4. Memory Check
        try:
            memory = psutil.virtual_memory()
            checks["checks"]["memory"] = {
                "status": "healthy" if memory.percent < 85 else "warning",
                "total_mb": round(memory.total / (1024**2), 2),
                "available_mb": round(memory.available / (1024**2), 2),
                "percent": memory.percent
            }
        except Exception as e:
            checks["checks"]["memory"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 5. R2 Storage Check (if enabled)
        if os.environ.get('R2_ACCESS_KEY_ID'):
            checks["checks"]["r2_storage"] = {
                "status": "enabled",
                "bucket": os.environ.get('R2_BUCKET_NAME', 'not-set')
            }
        else:
            checks["checks"]["r2_storage"] = {
                "status": "disabled"
            }
        
        # Determine overall status
        unhealthy_checks = [c for c in checks["checks"].values() 
                          if c.get("status") == "unhealthy"]
        warning_checks = [c for c in checks["checks"].values() 
                         if c.get("status") == "warning"]
        
        if unhealthy_checks:
            checks["status"] = "unhealthy"
            status_code = 503
        elif warning_checks:
            checks["status"] = "degraded"
            status_code = 200
        else:
            checks["status"] = "healthy"
            status_code = 200
        
        return JsonResponse(checks, status=status_code)


class SimpleHealthCheckView(View):
    """
    Simple health check for load balancers
    Returns 200 if app is running
    """
    
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            "status": "ok",
            "timestamp": timezone.now().isoformat()
        })