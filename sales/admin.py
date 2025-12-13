from django.contrib import admin
from .models import Purchase, ChargeCode, SubscriptionPackage

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'file', 'paid_price', 'timestamp']
    list_filter = ['timestamp']

@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'coin_value', 'price_dzd']

@admin.register(ChargeCode)
class ChargeCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'package', 'is_used', 'activated_by', 'created_at']
    list_filter = ['is_used']
