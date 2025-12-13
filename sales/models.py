from django.db import models
import random
import string
from accounts.models import Customer
from products.models import TechnicalFile
from django.utils import timezone

# ============ أكواد الشحن ============
def generate_charge_code():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=12))

class SubscriptionPackage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    coin_value = models.IntegerField() 
    price_dzd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.name} ({self.coin_value} Coins)"

class ChargeCode(models.Model):
    code = models.CharField(max_length=12, unique=True, default=generate_charge_code)
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    activated_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    activation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Code: {self.code} - {self.package.name}"

# ============ المشتريات ============
class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    file = models.ForeignKey(TechnicalFile, on_delete=models.CASCADE)
    paid_price = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    downloads_count = models.IntegerField(default=0)
    max_downloads = models.IntegerField(default=3)
    last_download_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Purchase #{self.id}"
    
    def can_download(self):
        return self.downloads_count < self.max_downloads
    
    def get_remaining_downloads(self):
        return max(0, self.max_downloads - self.downloads_count)
