# في notifications/admin.py
from django.contrib import admin
from .models import Notification

# تعريف فئة الإدارة لتنظيم العرض في اللوحة
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'title', 'is_read', 'timestamp')
    list_filter = ('is_read',)
    search_fields = ('customer__serial', 'title', 'message')
    
    # الإشعارات هي سجلات تاريخية، لا ينبغي تعديلها يدوياً.
    readonly_fields = ('customer', 'title', 'message', 'timestamp') 
    
    # ترتيب الإشعارات زمنياً (الأحدث أولاً)
    ordering = ('-timestamp',)
