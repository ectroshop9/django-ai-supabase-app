# في notifications/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer, MarkAsReadSerializer

# 1. عارض جلب قائمة الإشعارات (لعميل معين)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    # جلب الإشعارات التي تخص العميل المسجل دخوله فقط
    def get_queryset(self):
        return Notification.objects.filter(customer=self.request.user.customer).order_by('-timestamp')

# 2. عارض لتحديد إشعار واحد كمقروء
class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_id = serializer.validated_data['notification_id']
        customer = request.user.customer # العميل الحالي
        
        # البحث عن الإشعار الذي يخص العميل المطلوب تحديثه
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            customer=customer
        )
        
        notification.is_read = True
        notification.save()
        
        return Response({'message': 'تم وضع الإشعار كـ "مقروء" بنجاح.'}, status=status.HTTP_200_OK)