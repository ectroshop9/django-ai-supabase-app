import os
from datetime import datetime

def get_simple_stats():
    """بديل مبسط بدون psutil"""
    return {
        "status": "✅ نشط",
        "service": "Technical Files Store",
        "plan": "Render Free Tier (512MB)",
        "timestamp": datetime.now().isoformat(),
        "warning": "استخدم Supabase Storage للملفات الكبيرة",
        "note": "نظام الإحصائيات يعمل بدون psutil"
    }
