# في notifications/utils.py
from .models import Notification
from accounts.models import Customer

def create_notification(customer_instance: Customer, title: str, message: str):
    """دالة مساعدة لإنشاء إشعار جديد لعميل محدد."""
    Notification.objects.create(
        customer=customer_instance,
        title=title,
        message=message
    )