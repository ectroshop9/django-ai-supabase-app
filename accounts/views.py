# في accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics 
from rest_framework_simplejwt.views import TokenObtainPairView
# استيراد جميع الـ Serializers المطلوبة
from .serializers import (
    CustomTokenObtainPairSerializer, SerialRecoverySerializer, 
    TemporaryCreationSerializer, FinalActivationSerializer, 
    ReactivationSerializer, RechargeByCodeSerializer,
    WalletStatusSerializer
)
from .models import Customer

# **************************************************
# 1. مسارات المصادقة والدخول (Authentication)
# **************************************************

# عارض الدخول المخصص (يستخدم السيريال فقط)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# عارض استرداد السيريال (بالهاتف والبين)
class SerialRecoveryView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SerialRecoverySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# **************************************************
# 2. مسارات التفعيل على مرحلتين (Two-Stage Activation)
# **************************************************

# أ. إنشاء الحساب المؤقت (بعد تأكيد الدفع - يعطي Serial/Pin و JWT)
class TemporaryCreationView(generics.CreateAPIView):
    serializer_class = TemporaryCreationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        # نمرر بيانات فارغة لأن البيانات يتم توليدها في Serializer.save
        serializer = self.get_serializer(data={})
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)

# ب. التفعيل النهائي (إضافة البيانات وتفعيل is_active وإضافة الرصيد)
class FinalActivationView(generics.UpdateAPIView):
    serializer_class = FinalActivationSerializer
    permission_classes = [IsAuthenticated] 
    
    # يحدد كائن العميل المسجل دخوله (request.user) للتحديث
    def get_object(self):
        return self.request.user

# ج. إعادة التنشيط (بعد تجاوز مهلة الـ 48 ساعة)
class ReactivationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ReactivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# **************************************************
# 3. مسارات المحفظة (Wallet Operations)
# **************************************************

# أ. شحن الرصيد باستخدام كود الشحن
class RechargeByCodeView(generics.CreateAPIView):
    serializer_class = RechargeByCodeSerializer
    permission_classes = [IsAuthenticated] 
    
    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        # يجب تمرير request إلى السياق للوصول إلى العميل المسجل دخوله
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = self.perform_create(serializer)
        
        return Response(data, status=status.HTTP_200_OK)

# ب. جلب حالة الرصيد والمعاملات (حساب العميل)
class WalletStatusView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletStatusSerializer
    
    def get_object(self):
        # الحصول على كائن Wallet المرتبط بالعميل المسجل دخوله
        return self.request.user.wallet