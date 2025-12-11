# في products/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    PurchaseSerializer, PurchaseDetailSerializer,
    CategorySerializer, FileDetailSerializer
)
from .models import TechnicalFile, Category, Purchase

# **************************************************
# 1. مسارات عرض المتجر (Store Browsing)
# **************************************************

# أ. عارض جلب قائمة التصنيفات
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

# ب. عارض جلب قائمة الملفات ضمن تصنيف محدد
class FilesByCategoryView(generics.ListAPIView):
    serializer_class = FileDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        category_id = self.kwargs['category_id'] # جلب ID التصنيف من الرابط
        return TechnicalFile.objects.filter(
            category__id=category_id, 
            is_available=True
        ).select_related('category')


# **************************************************
# 2. مسارات الشراء وسجل المشتريات (Purchasing)
# **************************************************

# أ. عارض لمعالجة طلب الشراء (الخصم من الرصيد)
class PurchaseView(generics.CreateAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        # تمرير request إلى السياق للوصول إلى العميل
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        
        return Response(data, status=status.HTTP_200_OK)

# ب. عارض جلب قائمة الملفات التي اشتراها العميل
class PurchaseListView(generics.ListAPIView):
    serializer_class = PurchaseDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # جلب سجلات الشراء التي تخص العميل المسجل دخوله فقط
        return Purchase.objects.filter(customer=self.request.user.customer).order_by('-timestamp')