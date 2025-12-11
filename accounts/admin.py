# في accounts/admin.py
from django.contrib import admin
from .models import Customer, Wallet, Transaction
from django.db import IntegrityError

# دمج المحفظة (Wallet) مع العميل (Customer) في لوحة الإدارة (Inline)
class WalletInline(admin.StackedInline):
    model = Wallet
    can_delete = False
    # لمنع التعديل على الحقول المحسوبة تلقائياً
    readonly_fields = ('total_deposited', 'total_spent') 
    # السماح للمدير بتعديل الرصيد يدوياً (لشحن المباشر)
    fields = ('balance', 'total_deposited', 'total_spent')

# تسجيل نموذج العميل
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial', 'phone', 'is_active', 'created_at')
    search_fields = ('name', 'serial', 'phone')
    list_filter = ('is_active',)
    
    # منع التعديل اليدوي على السيريال والبين ووقت الإنشاء
    readonly_fields = ('serial', 'pin', 'created_at') 
    
    # عرض المحفظة مباشرة أسفل العميل
    inlines = [WalletInline] 

# تسجيل نموذج المعاملات
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type',)
    search_fields = ('customer__serial', 'customer__name', 'description')
    
    # المعاملة هي سجل تاريخي، يجب منع تعديلها بعد إنشائها
    readonly_fields = ('customer', 'amount', 'transaction_type', 'description', 'timestamp')