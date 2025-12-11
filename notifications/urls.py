# في notifications/urls.py
from django.urls import path
from .views import NotificationListView, MarkNotificationAsReadView

urlpatterns = [
    # 1. جلب جميع الإشعارات
    path('list/', NotificationListView.as_view(), name='notification_list'),
    
    # 2. وضع إشعار كـ "مقروء"
    path('mark-read/', MarkNotificationAsReadView.as_view(), name='mark_read'),
]