# في accounts/models.py
from django.db import models
import random
import string
from django.contrib.auth.models import User # لاستخدام نموذج المستخدم الافتراضي لـ JWT

# دالة لتوليد رمز PIN عشوائي مكون من 4 أرقام
def generate_pin():
    return ''.join(random.choices(string.digits, k=4))

# دالة لتوليد السيريال (Serial Key) بـ 15 حرف ورقم عشوائياً
def generate_serial():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=15)) 

class Customer(models.Model):
    # الطول 15 كما هو مطلوب
    serial = models.CharField(max_length=15, unique=True, default=generate_serial)
    pin = models.CharField(max_length=4, default=generate_pin)                      
    
    # السماح بأن تكون فارغة في مرحلة الإنشاء المؤقت
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    
    is_active = models.BooleanField(default=False) # غير نشط افتراضياً
    created_at = models.DateTimeField(auto_now_add=True) 
    
    # ربط العميل بكائن User الافتراضي لتشغيل SimpleJWT بشكل صحيح
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f"{self.serial} - {self.name or 'TEMP'}"

# نموذج Wallet (المحفظة)
class Wallet(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE) 
    balance = models.IntegerField(default=0)      
    total_deposited = models.IntegerField(default=0) 
    total_spent = models.IntegerField(default=0)     
    
    def __str__(self):
        return f"Wallet for {self.customer.serial} - Balance: {self.balance}"

# نموذج Transaction (المعاملة)
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INITIAL', 'تفعيل الباقة الأولية'),
        ('CHARGE', 'شحن رصيد'),
        ('PURCHASE', 'شراء ملفات'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)      
    amount = models.IntegerField()                                          
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES) 
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.serial} - {self.transaction_type} ({self.amount})"