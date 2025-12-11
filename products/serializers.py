# في products/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import TechnicalFile, Purchase, Category
from accounts.models import Wallet, Transaction
from notifications.utils import create_notification 

# 1. Serializer لعرض التصنيف
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')

# 2. Serializer لعرض تفاصيل الملف (للعرض في المتجر)
class FileDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = TechnicalFile
        fields = (
            'id', 'title', 'description', 
            'file_image', 'price_coins', 
            'category_name'
        )
        
# 3. Serializer لمعالجة عملية الشراء والخصم
class PurchaseSerializer(serializers.Serializer):
    file_id = serializers.IntegerField() # معرف الملف الذي يريد العميل شراءه

    def validate(self, attrs):
        file_id = attrs.get('file_id')
        customer = self.context['request'].user.customer
        
        # 1. التحقق من وجود الملف
        try:
            file_obj = TechnicalFile.objects.get(id=file_id, is_available=True)
        except TechnicalFile.DoesNotExist:
            raise serializers.ValidationError({"file_id": "الملف المطلوب غير موجود أو غير متاح."})
            
        # 2. التحقق من الرصيد
        wallet = customer.wallet 
        if wallet.balance < file_obj.price_coins:
            raise serializers.ValidationError({"balance": f"الرصيد غير كافٍ. يتطلب {file_obj.price_coins} كوين، رصيدك الحالي {wallet.balance}."})
            
        # 3. التحقق من تكرار الشراء
        if Purchase.objects.filter(customer=customer, file=file_obj).exists():
            raise serializers.ValidationError({"file_id": "لقد اشتريت هذا الملف بالفعل."})

        # تخزين الكائنات للاستخدام في دالة save
        self.file_obj = file_obj
        self.wallet = wallet
        self.customer = customer
        
        return attrs

    def save(self, **kwargs):
        # تنفيذ عملية الخصم والتسجيل داخل معاملة واحدة
        with transaction.atomic():
            
            # 1. الخصم من المحفظة
            self.wallet.balance -= self.file_obj.price_coins
            self.wallet.total_spent += self.file_obj.price_coins
            self.wallet.save()
            
            # 2. تسجيل عملية الشراء
            Purchase.objects.create(
                customer=self.customer,
                file=self.file_obj,
                paid_price=self.file_obj.price_coins
            )
            
            # 3. تسجيل معاملة الخصم
            Transaction.objects.create(
                customer=self.customer,
                amount=-self.file_obj.price_coins, # بالسالب لتمثيل الخصم
                transaction_type='PURCHASE',
                description=f"شراء الملف: {self.file_obj.title}"
            )
            
            # 4. تحفيز الإشعار
            create_notification(
                self.customer, 
                title="تم شراء ملف جديد",
                message=f"تم خصم {self.file_obj.price_coins} كوينز لشراء الملف '{self.file_obj.title}'. الرابط متاح في قائمة مشترياتك."
            )
            
            return {
                'file_url': self.file_obj.file_url,
                'new_balance': self.wallet.balance,
                'file_title': self.file_obj.title
            }

# 4. Serializer لعرض الملفات المشتراة (لتجنب عرض حقل file_url إلا بعد الشراء)
class PurchaseDetailSerializer(serializers.ModelSerializer):
    file_title = serializers.CharField(source='file.title')
    file_url = serializers.URLField(source='file.file_url')
    
    class Meta:
        model = Purchase
        fields = ('file_title', 'file_url', 'paid_price', 'timestamp')