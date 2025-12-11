# في notifications/models.py
from django.db import models
from accounts.models import Customer # استيراد نموذج العميل

class Notification(models.Model):
    # ربط الإشعار بالعميل المستهدف
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    
    # محتوى الإشعار
    title = models.CharField(max_length=150)
    message = models.TextField()
    
    # حالة الإشعار
    is_read = models.BooleanField(default=False)
    
    # وقت الإرسال
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp'] # الأحدث يظهر أولاً
        
    def __str__(self):
        return f"[{'READ' if self.is_read else 'NEW'}] {self.title} for {self.customer.serial}"