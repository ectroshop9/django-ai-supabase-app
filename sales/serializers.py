
from rest_framework import serializers
from django.db import transaction
from .models import Purchase, ChargeCode, SubscriptionPackage
from accounts.models import Wallet, Transaction
from notifications.utils import create_notification
import secrets
import requests
import time
from django.conf import settings
from django.utils import timezone
from products.models import TechnicalFile

# ===== Serializers الحالية (أكواد الشحن) =====
class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPackage
        fields = ['id', 'name', 'coin_value', 'price_dzd']
        read_only_fields = fields

class ChargeCodeSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source='package.name', read_only=True)
    package_coins = serializers.IntegerField(source='package.coin_value', read_only=True)
    activated_by_serial = serializers.CharField(source='activated_by.serial', read_only=True, allow_null=True)
    
    class Meta:
        model = ChargeCode
        fields = [
            'id', 'code', 'package', 'package_name', 'package_coins',
            'is_used', 'activated_by', 'activated_by_serial',
            'activation_date', 'created_at'
        ]
        read_only_fields = ['code', 'created_at']

# ===== Serializers الجديدة (الشراء والتحميل) =====
class PurchaseSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()

    def validate(self, attrs):
        file_id = attrs.get('file_id')
        customer = self.context['request'].user.customer
        
        try:
            file_obj = TechnicalFile.objects.get(id=file_id, is_available=True)
        except TechnicalFile.DoesNotExist:
            raise serializers.ValidationError({"file_id": "الملف غير موجود أو غير متاح"})
            
        wallet = customer.wallet 
        if wallet.balance < file_obj.price_coins:
            raise serializers.ValidationError({
                "balance": f"الرصيد غير كافٍ. يتطلب {file_obj.price_coins} كوين"
            })
            
        if Purchase.objects.filter(customer=customer, file=file_obj).exists():
            raise serializers.ValidationError({"file_id": "لقد اشتريت هذا الملف بالفعل"})

        self.file_obj = file_obj
        self.wallet = wallet
        self.customer = customer
        
        return attrs

    def save(self, **kwargs):
        purchase = None
        
        with transaction.atomic():
            self.wallet.balance -= self.file_obj.price_coins
            self.wallet.total_spent += self.file_obj.price_coins
            self.wallet.save()
            
            purchase = Purchase.objects.create(
                customer=self.customer,
                file=self.file_obj,
                paid_price=self.file_obj.price_coins
            )
            
            Transaction.objects.create(
                customer=self.customer,
                amount=-self.file_obj.price_coins,
                transaction_type='PURCHASE',
                description=f"شراء الملف: {self.file_obj.title}"
            )
            
            create_notification(
                self.customer, 
                title="تم شراء ملف جديد",
                message=f"تم شراء الملف '{self.file_obj.title}'"
            )
        
        return {
            'success': True,
            'purchase_id': purchase.id,
            'purchased_at': purchase.timestamp,
            'file_title': self.file_obj.title,
            'file_price': self.file_obj.price_coins,
            'new_balance': self.wallet.balance,
            'instructions': 'اذهب إلى مشترياتك لتحميل الملف'
        }

class PurchaseDetailSerializer(serializers.ModelSerializer):
    file_title = serializers.CharField(source='file.title')
    file_id = serializers.IntegerField(source='file.id')
    can_download = serializers.SerializerMethodField()
    downloads_left = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase
        fields = ('id', 'file_title', 'file_id', 'paid_price', 
                 'timestamp', 'downloads_count', 'can_download', 'downloads_left')
    
    def get_can_download(self, obj):
        return obj.downloads_count < 3
    
    def get_downloads_left(self, obj):
        return max(0, 3 - obj.downloads_count)

class DownloadSerializer(serializers.Serializer):
    purchase_id = serializers.IntegerField()
    
    def validate(self, attrs):
        purchase_id = attrs.get('purchase_id')
        customer = self.context['request'].user.customer
        
        try:
            purchase = Purchase.objects.get(id=purchase_id, customer=customer)
        except Purchase.DoesNotExist:
            raise serializers.ValidationError({"purchase_id": "الشراء غير موجود"})
            
        if purchase.downloads_count >= 3:
            raise serializers.ValidationError({"downloads": "تم استنفاذ التحميلات"})
            
        self.purchase = purchase
        self.customer = customer
        
        return attrs
