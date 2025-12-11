# في notifications/serializers.py
from rest_framework import serializers
from .models import Notification

# Serializer لعرض بيانات الإشعار
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        # لا نعرض حقل العميل لأنه سيتم جلبه تلقائياً
        fields = ('id', 'title', 'message', 'is_read', 'timestamp')
        read_only_fields = ('id', 'timestamp')
        
# Serializer لتحديث حالة is_read (لجعل الإشعار مقروءاً)
class MarkAsReadSerializer(serializers.Serializer):
    notification_id = serializers.IntegerField()