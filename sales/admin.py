# في sales/admin.py
from django.contrib import admin
from .models import SubscriptionPackage, ChargeCode

@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'coin_value', 'price_dzd')

@admin.register(ChargeCode)
class ChargeCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'package', 'is_used', 'activated_by', 'activation_date', 'created_at')
    list_filter = ('is_used', 'package')
    search_fields = ('code', 'activated_by__serial')
    
    # منع التعديل اليدوي على الكود الذي يتم توليده
    readonly_fields = ('code', 'created_at', 'activation_date', 'activated_by')

# Register your models here.
