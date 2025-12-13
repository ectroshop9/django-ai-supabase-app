from rest_framework import serializers
from .models import SubscriptionPackage, ChargeCode
from accounts.models import Customer

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

class GenerateChargeCodeSerializer(serializers.Serializer):
    package_id = serializers.IntegerField()
    count = serializers.IntegerField(min_value=1, max_value=100, default=1)
    
    def validate_package_id(self, value):
        try:
            SubscriptionPackage.objects.get(id=value)
        except SubscriptionPackage.DoesNotExist:
            raise serializers.ValidationError("الباقة غير موجودة")
        return value

class DirectRechargeSerializer(serializers.Serializer):
    customer_serial = serializers.CharField(max_length=15)
    coin_amount = serializers.IntegerField(min_value=1, max_value=100000)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_customer_serial(self, value):
        try:
            Customer.objects.get(serial=value)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("رقم السيريال غير صحيح")
        return value

class PackageActivationSerializer(serializers.Serializer):
    package_id = serializers.IntegerField()
    customer_name = serializers.CharField(max_length=100, required=False, default="عميل")
    customer_phone = serializers.CharField(max_length=15, required=False, allow_null=True)
    
    def validate_package_id(self, value):
        try:
            SubscriptionPackage.objects.get(id=value)
        except SubscriptionPackage.DoesNotExist:
            raise serializers.ValidationError("الباقة غير موجودة")
        return value
    
    def validate_customer_phone(self, value):
        if value and Customer.objects.filter(phone=value).exists():
            raise serializers.ValidationError("رقم الهاتف مسجل بالفعل")
        return value

class CheckCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12)
