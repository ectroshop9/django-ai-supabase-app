# في accounts/serializers.py
from rest_framework import serializers
from .models import Customer, Wallet, Transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

# [ملاحظة]: يجب التأكد من وجود هذه الملفات والوحدات ليعمل الكود
from sales.models import ChargeCode 
from notifications.utils import create_notification 

# **************************************************
# I. السيريالايزر الخاصة بالمصادقة (JWT & Login)
# **************************************************

# 1. تخصيص الدخول: استخدام السيريال (Serial) بدلاً من اسم المستخدم
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # نغير الحقل الأساسي من 'username' إلى 'serial'
    default_field_names = ['serial']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        del self.fields['password'] # لا نحتاج إلى كلمة مرور

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # إضافة بيانات العميل إلى التوكن (Payload)
        try:
            customer = user.customer
            token['serial'] = customer.serial
            token['is_active'] = customer.is_active
        except Customer.DoesNotExist:
            # في حال كان المستخدم هو مدير Django وليس عميلاً
            pass 
        return token

    def validate(self, attrs):
        serial = attrs.get('serial')

        try:
            customer = Customer.objects.get(serial=serial)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Serial غير صالح.")
        
        if not customer.is_active:
            # إذا كان الحساب غير نشط (مؤقت أو معلق)، يرفض الدخول
            raise serializers.ValidationError("الحساب غير نشط. يرجى إتمام عملية التفعيل.")
        
        # SimpleJWT يتطلب كائن User، لذا نستخدم كائن User المرتبط
        user = customer.user 

        if user is None:
            # يجب أن يكون لكل عميل كائن User مرتبط (يتم إنشاؤه في TemporaryCreationSerializer)
            raise serializers.ValidationError("خطأ في النظام: لا يوجد حساب مستخدم مرتبط.")
        
        # إتمام عملية الدخول للحصول على التوكن
        refresh = self.get_token(user)

        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # إضافة بيانات العميل إلى الرد
        data['serial'] = customer.serial
        data['name'] = customer.name
        data['is_active'] = customer.is_active

        return data

# 2. استرداد السيريال (بالهاتف والبين)
class SerialRecoverySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    pin = serializers.CharField(max_length=4)
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        pin = attrs.get('pin')
        
        try:
            customer = Customer.objects.get(phone=phone, pin=pin)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("رقم الهاتف أو البين كود غير صحيح.")
        
        return {
            'serial': customer.serial,
            'message': 'تم استرداد السيريال بنجاح.'
        }


# **************************************************
# II. السيريالايزر الخاصة بالتفعيل على مرحلتين
# **************************************************

# 3. الإنشاء المؤقت (Temporary Creation)
class TemporaryCreationSerializer(serializers.Serializer):
    
    def create(self, validated_data):
        # 1. إنشاء كائن User (اللازم لـ JWT)
        # نستخدم اسم مستخدم وهمي فريد هنا (يمكن أن يكون السيريال نفسه)
        temp_username = f"temp_{timezone.now().timestamp()}_{random.randint(1000, 9999)}"
        user = User.objects.create_user(username=temp_username) 
        user.is_active = False # تعطيل المستخدم مؤقتاً في User Model أيضاً
        user.save()
        
        # 2. إنشاء العميل المؤقت (Serial, Pin يتولد، Name/Phone فارغين)
        # is_active = False افتراضياً
        customer = Customer.objects.create(user=user) 
        
        # 3. إنشاء محفظة Wallet للعميل
        Wallet.objects.create(customer=customer)
        
        # 4. منح توكن JWT للدخول المؤقت
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'serial': customer.serial,
            'pin': customer.pin,
            'customer_id': customer.id,
            'message': 'تم إنشاء حساب مؤقت بنجاح. يرجى إتمام بياناتك للتفعيل النهائي.'
        }

# 4. التفعيل النهائي (Final Activation)
class FinalActivationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=15)
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        customer = self.context['request'].user.customer # العميل المسجل دخوله حالياً
        
        # التحقق من أن رقم الهاتف لم يُسجل من قبل في أي حساب آخر
        if Customer.objects.filter(phone=phone).exclude(id=customer.id).exists():
            raise serializers.ValidationError({"phone": "رقم الهاتف مُسجل بالفعل في حساب آخر."})
        
        # [مهم] التحقق من تجاوز مهلة الـ 48 ساعة
        time_elapsed = timezone.now() - customer.created_at
        if time_elapsed > timedelta(hours=48) and customer.name is None: 
            raise serializers.ValidationError({
                "detail": "انتهت فترة الـ 48 ساعة. يرجى إعادة تنشيط حسابك باستخدام البين كود أولاً.",
                "action": "reactivate" 
            })

        return attrs

    def update(self, instance, validated_data):
        # instance هنا هو كائن User المرتبط بالعميل
        customer = instance.customer
        
        # 1. تحديث بيانات العميل وتفعيله
        customer.name = validated_data.get('name', customer.name)
        customer.phone = validated_data.get('phone', customer.phone)
        customer.is_active = True # تفعيل الحساب
        customer.save()
        
        # تفعيل كائن المستخدم أيضاً
        instance.is_active = True
        instance.save()
        
        # 2. إضافة الرصيد الأولي 
        wallet = customer.wallet 
        initial_balance = 100 
        
        with transaction.atomic():
            wallet.balance += initial_balance
            wallet.total_deposited += initial_balance
            wallet.save()
            
            # 3. تسجيل المعاملة
            Transaction.objects.create(
                customer=customer,
                amount=initial_balance,
                transaction_type='INITIAL',
                description="تفعيل الحساب الأولي بعد إضافة البيانات الشخصية"
            )
            
            # 4. إرسال الإشعار
            create_notification(
                customer, 
                title="تم تفعيل حسابك بنجاح",
                message=f"مرحباً بك، تم إضافة {initial_balance} كوينز كرصيد تفعيل أولي إلى محفظتك."
            )
        
        return customer # نُرجع كائن العميل

# 5. إعادة التنشيط (Re-Activation)
class ReactivationSerializer(serializers.Serializer):
    serial = serializers.CharField(max_length=15)
    pin = serializers.CharField(max_length=4)

    def validate(self, attrs):
        serial = attrs.get('serial')
        pin = attrs.get('pin')
        
        try:
            customer = Customer.objects.get(serial=serial, pin=pin)
        except Customer.DoesNotExist:
            raise serializers.ValidationError("السيريال أو البين غير صحيح.")

        if customer.is_active:
            raise serializers.ValidationError("الحساب نشط بالفعل ولا يحتاج لإعادة تنشيط.")

        time_elapsed = timezone.now() - customer.created_at
        if time_elapsed < timedelta(hours=48):
             raise serializers.ValidationError("لا يمكن إعادة تنشيط الحساب قبل انتهاء فترة السماح (48 ساعة).")

        # إعادة تنشيطه مؤقتاً في كلا النموذجين
        customer.is_active = True
        customer.save()
        customer.user.is_active = True
        customer.user.save()
        
        # منح توكن JWT للدخول الفوري بعد التنشيط
        refresh = RefreshToken.for_user(customer.user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'serial': customer.serial,
            'message': 'تم تنشيط الحساب بنجاح. يرجى المتابعة لإتمام بياناتك.'
        }


# **************************************************
# III. السيريالايزر الخاصة بالمحفظة والمعاملات (Wallet)
# **************************************************

# 6. شحن الرصيد بكود الشحن
class RechargeByCodeSerializer(serializers.Serializer):
    charge_code = serializers.CharField(max_length=12)

    def validate(self, attrs):
        code = attrs.get('charge_code')
        
        try:
            # يجب أن يكون ChargeCode مرتبطاً بـ SubscriptionPackage عبر foreign key
            charge_code_obj = ChargeCode.objects.select_related('package').get(code=code)
        except ChargeCode.DoesNotExist:
            raise serializers.ValidationError({"charge_code": "كود الشحن غير صالح."})
            
        if charge_code_obj.is_used:
            raise serializers.ValidationError({"charge_code": "هذا الكود تم استخدامه بالفعل."})

        self.recharge_value = charge_code_obj.package.coin_value
        self.charge_code_obj = charge_code_obj
        
        return attrs

    def save(self, **kwargs):
        customer = self.context['request'].user.customer # العميل المسجل دخوله
        wallet = customer.wallet 
        
        with transaction.atomic():
            # 1. تحديث حالة كود الشحن
            self.charge_code_obj.is_used = True
            self.charge_code_obj.activated_by = customer
            self.charge_code_obj.activation_date = timezone.now()
            self.charge_code_obj.save()
            
            # 2. تحديث رصيد المحفظة
            wallet.balance += self.recharge_value
            wallet.total_deposited += self.recharge_value
            wallet.save()
            
            # 3. تسجيل المعاملة
            Transaction.objects.create(
                customer=customer,
                amount=self.recharge_value,
                transaction_type='CHARGE',
                description=f"شحن رصيد بواسطة الكود: {self.charge_code_obj.code}"
            )
            
            # 4. تحفيز الإشعار
            create_notification(
                customer, 
                title="تم شحن الرصيد بنجاح!",
                message=f"تم إضافة {self.recharge_value} كوينز إلى محفظتك. رصيدك الحالي: {wallet.balance}."
            )
            
            return {
                'new_balance': wallet.balance,
                'recharged_amount': self.recharge_value,
                'message': 'تم شحن الحساب بنجاح.'
            }


# 7. Serializer لعرض بيانات المعاملة (لتضمينها في حالة المحفظة)
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('amount', 'transaction_type', 'description', 'timestamp')


# 8. Serializer لعرض حالة المحفظة الكاملة
class WalletStatusSerializer(serializers.ModelSerializer):
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ('balance', 'total_deposited', 'total_spent', 'recent_transactions')
        
    def get_recent_transactions(self, obj):
        # obj هو كائن Wallet
        # جلب آخر 10 معاملات لهذا العميل
        transactions = Transaction.objects.filter(customer=obj.customer).order_by('-timestamp')[:10]
        return TransactionSerializer(transactions, many=True).data