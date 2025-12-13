from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Purchase
from .utils.worker_client import CloudflareWorkerClient
from notifications.utils import create_notification
from .serializers import PurchaseSerializer, DownloadSerializer, PurchaseDetailSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchase_file(request):
    """شراء ملف جديد"""
    serializer = PurchaseSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_download(request, purchase_id):
    """إنشاء رابط تحميل عند الضغط على زر التحميل"""
    customer = request.user.customer
    
    # البحث عن الشراء
    try:
        purchase = Purchase.objects.get(id=purchase_id, customer=customer)
    except Purchase.DoesNotExist:
        return Response({"error": "الشراء غير موجود"}, status=404)
    
    # التحقق من إمكانية التحميل
    if not purchase.can_download():
        return Response({
            "error": "تم استنفاذ التحميلات",
            "remaining": 0
        }, status=400)
    
    # إنشاء رابط محمي
    worker = CloudflareWorkerClient()
    download_url = worker.create_protected_link(
        file_url=purchase.file.file_url,
        metadata={
            'purchase_id': purchase.id,
            'customer_id': customer.id
        }
    )
    
    if not download_url.get('success'):
        return Response({"error": download_url.get('error', 'فشل إنشاء الرابط')}, status=500)
    
    # تحديث الإحصائيات
    purchase.downloads_count += 1
    purchase.last_download_at = timezone.now()
    purchase.save()
    
    # إرجاع الرابط للمستخدم
    return Response({
        "success": True,
        "download_url": download_url.get('download_url'),
        "expires_in": "ساعتين",
        "remaining_downloads": purchase.get_remaining_downloads()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_purchases(request):
    """عرض مشتريات المستخدم"""
    purchases = Purchase.objects.filter(customer=request.user.customer)
    serializer = PurchaseDetailSerializer(purchases, many=True)
    return Response(serializer.data)