# في sales/models.py
from django.db import models
import random
import string
from accounts.models import Customer # ربط كود الشحن بالعميل الذي قام بتفعيله

# دالة لتوليد كود شحن عشوائي مكون من 12 حرف ورقم
def generate_charge_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=12))

# 1. نموذج SubscriptionPackage (الباقات)
class SubscriptionPackage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # قيمة الكوينات التي يحصل عليها العميل من هذه الباقة
    coin_value = models.IntegerField() 
    price_dzd = models.DecimalField(max_digits=10, decimal_places=2, default=0) # السعر بالدينار

    def __str__(self):
        return f"{self.name} ({self.coin_value} Coins)"

# 2. نموذج ChargeCode (أكواد الشحن)
class ChargeCode(models.Model):
    code = models.CharField(max_length=12, unique=True, default=generate_charge_code)
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE)
    
    is_used = models.BooleanField(default=False)
    # تسجيل العميل الذي قام بتفعيل الكود
    activated_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    activation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Code: {self.code} - {self.package.name} ({'USED' if self.is_used else 'NEW'})"
